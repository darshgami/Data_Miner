import { useState } from 'react';
import * as XLSX from 'xlsx';

function App() {
  const [city, setCity] = useState('');
  const [pincode, setPincode] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSearch = async () => {
    if (!city) return;

    setIsSearching(true);
    setErrorMsg('');
    setResults([]);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/search/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city, pincode })
      });

      const data = await res.json();

      if (data && data.length > 0) {
        setResults(data);
      } else {
        setErrorMsg("No data found.");
      }

    } catch (err) {
      setErrorMsg("Backend connection failed.");
    }

    setIsSearching(false);
  };

  const handleScrapeCurrentPage = async () => {
    setIsSearching(true);
    setErrorMsg('');
    
    try {
      if (typeof chrome === 'undefined' || !chrome.tabs) {
        setErrorMsg("Chrome extension API not available.");
        setIsSearching(false);
        return;
      }

      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab) {
        setErrorMsg("No active tab found.");
        setIsSearching(false);
        return;
      }

      chrome.tabs.sendMessage(tab.id, { action: "scrape_page" }, (response) => {
        setIsSearching(false);
        if (chrome.runtime.lastError) {
          setErrorMsg("Could not connect to the page. Please refresh the page and try again.");
          return;
        }

        if (response && response.success && response.data.length > 0) {
          // Format data to match backend results format
          const formattedData = response.data.map(item => ({
            company: item.name,
            email: item.email,
            phone: item.phone,
            address: item.address,
            url: item.url
          }));
          
          setResults(prev => {
            const currentIdentifiers = new Set(prev.map(r => `${r.email}-${r.phone}`));
            const newUnique = formattedData.filter(r => !currentIdentifiers.has(`${r.email}-${r.phone}`));
            return [...newUnique, ...prev];
          });
        } else if (response && !response.success) {
          setErrorMsg(response.error || "Failed to extract data.");
        } else {
          setErrorMsg("No valid contact data found on this page.");
        }
      });
    } catch (err) {
      setIsSearching(false);
      setErrorMsg("Error accessing tab.");
    }
  };

  const handleDownloadCSV = () => {
    if (results.length === 0) return;
    const headers = ['Company Name', 'Email', 'Phone No', 'URL', 'Address'];
    const rows = results.map(r => [
      `"${r.company || ''}"`,
      `"${r.email || ''}"`,
      `"${r.phone || ''}"`,
      `"${r.url || ''}"`,
      `"${r.address || ''}"`
    ]);
    
    const csvContent = [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `leads_${city}${pincode ? '_' + pincode : ''}.csv`;
    link.click();
  };

  const handleDownloadExcel = () => {
    if (results.length === 0) return;
    const wsData = results.map(r => ({
      'Company Name': r.company,
      'Email': r.email,
      'Phone No': r.phone,
      'URL': r.url,
      'Address': r.address
    }));
    const ws = XLSX.utils.json_to_sheet(wsData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Leads");
    XLSX.writeFile(wb, `leads_${city}${pincode ? '_' + pincode : ''}.xlsx`);
  };

  return (
    <div className="flex flex-col bg-white text-slate-800 shadow-xl overflow-hidden font-sans border border-slate-200" style={{width: '400px', minHeight: '550px', maxHeight: '600px'}}>
      
      {/* HEADER */}
      <div className="bg-white border-b border-slate-200 p-4 flex flex-col justify-center items-center text-center">
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Business Lead Extractor</h1>
        <p className="text-sm text-blue-600 font-medium mt-1">Deep Scraping Active</p>
      </div>

      {/* INPUT SECTION */}
      <div className="p-4 bg-slate-50 flex flex-col gap-3 border-b border-slate-200">
        <div className="flex gap-3">
          <input 
            type="text" 
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="flex-1 bg-white border border-slate-300 text-slate-800 text-sm rounded-md px-3 py-2.5 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 shadow-sm"
            placeholder="Target City (Required)"
          />
          <input 
            type="text" 
            value={pincode}
            onChange={(e) => setPincode(e.target.value)}
            className="w-32 bg-white border border-slate-300 text-slate-800 text-sm rounded-md px-3 py-2.5 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 shadow-sm"
            placeholder="Pincode (Optional)"
          />
        </div>

        {errorMsg && (
          <div className="p-2.5 bg-red-50 border border-red-200 rounded-md text-red-600 text-xs font-medium">
            {errorMsg}
          </div>
        )}

        <div className="flex flex-col gap-2">
          <button 
            onClick={handleSearch}
            disabled={isSearching || !city}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 shadow-sm"
          >
            {isSearching && city ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin h-4 w-4 border-2 border-white/30 border-t-white rounded-full"></span>
                Searching...
              </span>
            ) : (
              "Search Backend API"
            )}
          </button>
          
          <button 
            onClick={handleScrapeCurrentPage}
            disabled={isSearching}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 shadow-sm"
          >
            {isSearching && !city ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin h-4 w-4 border-2 border-white/30 border-t-white rounded-full"></span>
                Scraping Page...
              </span>
            ) : (
              "Scrape Current Page"
            )}
          </button>
        </div>
      </div>

      {/* RESULTS SECTION */}
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 bg-white custom-scrollbar">
        {results.length > 0 ? (
          <div className="flex flex-col gap-3">
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{results.length} Leads Processed</span>
            </div>
            {results.map((item, index) => (
              <div key={index} className="p-3 bg-white border border-slate-200 rounded-md shadow-sm hover:border-blue-300 transition-colors">
                <h2 className="font-semibold text-slate-900 text-sm mb-1 truncate">{item.company}</h2>
                <div className="flex flex-col gap-1">
                  <a href={item.url} target="_blank" rel="noreferrer" className="text-xs text-blue-600 hover:underline truncate">
                    {item.url}
                  </a>
                  <div className="grid grid-cols-2 gap-2 mt-1">
                    <span className="text-[11px] text-slate-600 truncate">📧 {item.email || 'N/A'}</span>
                    <span className="text-[11px] text-slate-600 truncate">📞 {item.phone || 'N/A'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center py-8">
            <p className="text-sm text-slate-500">Enter a City and Pincode<br/>and click Extract to search IndiaMART.</p>
          </div>
        )}
      </div>

      {/* EXPORT FOOTER */}
      {results.length > 0 && (
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex gap-3">
          <button 
            onClick={handleDownloadCSV}
            className="flex-1 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 font-medium py-2 rounded-md transition-colors text-sm shadow-sm"
          >
            Download .CSV
          </button>
          <button 
            onClick={handleDownloadExcel}
            className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 rounded-md transition-colors text-sm shadow-sm"
          >
            Download Excel
          </button>
        </div>
      )}
      
      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #f8fafc; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 10px; }
      `}</style>
    </div>
  );
}

export default App;

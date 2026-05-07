// content.js
// Chrome Extension content script for extracting structured business contact data

const cleanText = (text) => {
  if (!text) return '';
  // Remove non-printable characters, extra spaces, tabs, newlines
  return text.replace(/[\r\n\t]+/g, ' ')
             .replace(/[^a-zA-Z0-9\s,.'"-()&@:]/g, ' ')
             .replace(/\s+/g, ' ')
             .trim();
};

const isVisible = (element) => {
  if (!element || element.nodeType !== 1) return false;
  const style = window.getComputedStyle(element);
  return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && element.offsetWidth > 0 && element.offsetHeight > 0;
};

const extractEmails = (text) => {
  if (!text) return [];
  const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
  const emails = text.match(emailRegex) || [];
  
  return [...new Set(emails.map(e => e.toLowerCase()))].filter(email => {
    const invalidDomains = ['example.com', 'test.com', 'domain.com', 'email.com', 'yourdomain.com', 'mysite.com'];
    const invalidPrefixes = ['example', 'test', 'fake', 'info@example', 'noreply', 'no-reply'];
    const domain = email.split('@')[1];
    
    if (!domain) return false;
    if (invalidDomains.includes(domain)) return false;
    if (invalidPrefixes.some(prefix => email.startsWith(prefix + '@'))) return false;
    
    return true;
  });
};

const extractPhones = (text) => {
  if (!text) return [];
  // Matches international and local formats, allowing spaces, dashes, parentheses
  // Looking for at least 7 digits in total
  const phoneRegex = /(?:(?:\+|00)\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}[\s-]?\d{0,4}/g;
  const phones = text.match(phoneRegex) || [];
  
  return [...new Set(phones.map(p => p.trim()))].filter(phone => {
    const digitCount = phone.replace(/[^\d]/g, '').length;
    // Valid phone numbers are usually between 8 and 15 digits
    return digitCount >= 8 && digitCount <= 15 && !/^0{8,}$/.test(phone.replace(/[^\d]/g, ''));
  });
};

const isGenericName = (name) => {
  const genericTerms = ['home', 'contact', 'about', 'login', 'signup', 'register', 'menu', 'search', 'privacy policy', 'terms', 'services'];
  const lowerName = name.toLowerCase();
  return genericTerms.some(term => lowerName === term || lowerName.includes(` ${term} `));
};

const extractName = (element) => {
  if (!element) return '';
  const headings = element.querySelectorAll('h1, h2, h3, .profile-name, .company-name, .title');
  for (const h of headings) {
    if (isVisible(h)) {
      const text = cleanText(h.textContent);
      if (text && text.length > 2 && text.length < 100 && !isGenericName(text)) {
        return text;
      }
    }
  }
  
  // Fallback to title
  if (element === document.body) {
    const titleText = cleanText(document.title.split(/[-|]/)[0]);
    if (titleText && !isGenericName(titleText)) return titleText;
  }
  
  return '';
};

const extractAddress = (element) => {
  if (!element) return '';
  
  // Look for semantic address tags
  const addressTags = element.querySelectorAll('address');
  for (const tag of addressTags) {
    if (isVisible(tag)) {
      const text = cleanText(tag.textContent);
      if (text.length > 10) return text;
    }
  }

  // Look for common keywords
  const possibleElements = element.querySelectorAll('p, div, span, li');
  for (const el of possibleElements) {
    if (!isVisible(el)) continue;
    
    // Avoid checking large containers
    if (el.textContent.length > 500) continue;
    
    const text = el.textContent.toLowerCase();
    if (text.includes('address:') || text.includes('location:') || text.includes('hq:') || text.includes('headquarters:')) {
      const cleanedText = cleanText(el.textContent);
      // Try to remove the prefix and get the actual address
      const formatted = cleanedText.replace(/^(address|location|hq|headquarters|office)[\s]*:/i, '').trim();
      if (formatted.length > 5 && formatted.length < 200) {
        return formatted;
      }
    }
  }

  return '';
};

// Ignore irrelevant elements
const removeIrrelevantElements = (clone) => {
  const selectorsToRemove = [
    'script', 'style', 'noscript', 'iframe', 'svg', 'canvas',
    'nav', 'footer', 'header', '#cookie-banner', '.ad', '.ads',
    '[id*="google_ads"]', '[class*="advertisement"]', '.popup', '.modal'
  ];
  
  selectorsToRemove.forEach(selector => {
    const elements = clone.querySelectorAll(selector);
    elements.forEach(el => el.remove());
  });
  
  return clone;
};

const scrapePage = () => {
  console.log("Scraping started on:", window.location.href);
  const data = [];
  
  // Clone body to manipulate without affecting the page
  const bodyClone = document.body.cloneNode(true);
  const cleanedBody = removeIrrelevantElements(bodyClone);
  const bodyText = cleanedBody.innerText || cleanedBody.textContent;

  // Global extraction first as a fallback
  const globalEmails = extractEmails(bodyText);
  const globalPhones = extractPhones(bodyText);

  // Attempt to find specific sections
  const listingSelectors = [
    'article', '[itemtype*="Organization"]', '[itemtype*="LocalBusiness"]',
    '.listing', '.profile-card', '.company-item', '.business-card', '.contact-info', '.vcard'
  ];
  
  // Find visible matching elements in the actual DOM to check visibility properly
  let listingElements = [];
  for (const selector of listingSelectors) {
    try {
      const els = document.querySelectorAll(selector);
      for (const el of els) {
        if (isVisible(el)) {
           // Ensure it's not a huge wrapper element like the main layout
           if (el.innerText.length < 3000) {
              listingElements.push(el);
           }
        }
      }
    } catch (e) {
      // Ignore invalid selectors
    }
  }
  
  const uniqueListings = new Set(listingElements);

  if (uniqueListings.size > 0) {
    // Process multiple listings
    uniqueListings.forEach(el => {
      // Use textContent directly or innerText for visible text
      const text = el.innerText || el.textContent;
      const emails = extractEmails(text);
      const phones = extractPhones(text);
      const name = extractName(el);
      const address = extractAddress(el);

      // Only add if we found something useful
      if ((emails.length > 0 || phones.length > 0) || (name && address)) {
        data.push({
          name: name || "Unknown Contact",
          email: emails.length > 0 ? emails[0] : "",
          phone: phones.length > 0 ? phones[0] : "",
          address: address || "",
          url: window.location.href
        });
      }
    });
  } 

  // If no specific listings were found, or we want to capture the main page info
  if (data.length === 0) {
    // Single page profile or generic contact page
    const name = extractName(document.body);
    const address = extractAddress(document.body);

    if (globalEmails.length > 0 || globalPhones.length > 0 || address) {
        const maxItems = Math.max(globalEmails.length, globalPhones.length, 1);
        for (let i = 0; i < maxItems; i++) {
            if (globalEmails[i] || globalPhones[i] || (i === 0 && address)) {
                data.push({
                    name: i === 0 && name ? name : (name || "Contact"),
                    email: globalEmails[i] || "",
                    phone: globalPhones[i] || "",
                    address: i === 0 ? address : "",
                    url: window.location.href
                });
            }
        }
    }
  }

  // Deduplicate and validate final results
  const uniqueData = [];
  const seen = new Set();
  
  data.forEach(item => {
      // Must have at least one valid contact method (email or phone) to be considered useful
      // Or an address with a name
      if (!item.email && !item.phone && (!item.name || !item.address)) {
          return;
      }

      const identifier = `${item.email}-${item.phone}`.toLowerCase();
      
      // If no email or phone, use name and address as identifier
      const fallbackId = `${item.name}-${item.address}`.toLowerCase();
      
      const finalId = (identifier !== "-") ? identifier : fallbackId;

      if (!seen.has(finalId)) {
          seen.add(finalId);
          uniqueData.push({
             name: cleanText(item.name),
             email: item.email,
             phone: cleanText(item.phone),
             address: cleanText(item.address),
             url: item.url
          });
      }
  });

  return uniqueData;
};

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "scrape_page") {
    try {
      const results = scrapePage();
      sendResponse({ success: true, data: results });
    } catch (error) {
      console.error("Scraping error:", error);
      sendResponse({ success: false, error: error.message });
    }
  }
  return true;
});

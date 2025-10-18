export interface ScrapedItem {
  id: string;
  competitor: "fashionbug" | "coolplanet";
  clothingType: "men" | "women";
  clothingSubtype: "shirt" | "tshirt" | "skirt" | "jean" | "trouser" | "saree" | "frock";
  name: string;
  price: number;
  color: string;
  dateScraped: string;
}

export const mockData: ScrapedItem[] = [
  { id: "1", competitor: "fashionbug", clothingType: "men", clothingSubtype: "shirt", name: "Classic Cotton Shirt", price: 2500, color: "Blue", dateScraped: "2024-01-15" },
  { id: "2", competitor: "fashionbug", clothingType: "men", clothingSubtype: "tshirt", name: "Casual T-Shirt", price: 1200, color: "White", dateScraped: "2024-01-15" },
  { id: "3", competitor: "fashionbug", clothingType: "men", clothingSubtype: "jean", name: "Slim Fit Jeans", price: 3500, color: "Black", dateScraped: "2024-01-16" },
  { id: "4", competitor: "fashionbug", clothingType: "men", clothingSubtype: "trouser", name: "Formal Trousers", price: 2800, color: "Grey", dateScraped: "2024-01-16" },
  { id: "5", competitor: "fashionbug", clothingType: "women", clothingSubtype: "shirt", name: "Business Shirt", price: 2300, color: "Pink", dateScraped: "2024-01-17" },
  { id: "6", competitor: "fashionbug", clothingType: "women", clothingSubtype: "skirt", name: "Midi Skirt", price: 2000, color: "Red", dateScraped: "2024-01-17" },
  { id: "7", competitor: "fashionbug", clothingType: "women", clothingSubtype: "saree", name: "Traditional Saree", price: 4500, color: "Purple", dateScraped: "2024-01-18" },
  { id: "8", competitor: "fashionbug", clothingType: "women", clothingSubtype: "frock", name: "Summer Frock", price: 2200, color: "Yellow", dateScraped: "2024-01-18" },
  
  { id: "9", competitor: "coolplanet", clothingType: "men", clothingSubtype: "shirt", name: "Premium Shirt", price: 2800, color: "Blue", dateScraped: "2024-01-15" },
  { id: "10", competitor: "coolplanet", clothingType: "men", clothingSubtype: "tshirt", name: "Graphic Tee", price: 1500, color: "Black", dateScraped: "2024-01-15" },
  { id: "11", competitor: "coolplanet", clothingType: "men", clothingSubtype: "jean", name: "Denim Jeans", price: 3200, color: "Blue", dateScraped: "2024-01-16" },
  { id: "12", competitor: "coolplanet", clothingType: "men", clothingSubtype: "trouser", name: "Chino Pants", price: 2600, color: "Beige", dateScraped: "2024-01-16" },
  { id: "13", competitor: "coolplanet", clothingType: "women", clothingSubtype: "shirt", name: "Casual Blouse", price: 2100, color: "White", dateScraped: "2024-01-17" },
  { id: "14", competitor: "coolplanet", clothingType: "women", clothingSubtype: "skirt", name: "A-Line Skirt", price: 1800, color: "Black", dateScraped: "2024-01-17" },
  { id: "15", competitor: "coolplanet", clothingType: "women", clothingSubtype: "saree", name: "Silk Saree", price: 5000, color: "Green", dateScraped: "2024-01-18" },
  { id: "16", competitor: "coolplanet", clothingType: "women", clothingSubtype: "frock", name: "Floral Frock", price: 2400, color: "Pink", dateScraped: "2024-01-18" },
  
  { id: "17", competitor: "fashionbug", clothingType: "men", clothingSubtype: "shirt", name: "Linen Shirt", price: 2700, color: "White", dateScraped: "2024-01-19" },
  { id: "18", competitor: "fashionbug", clothingType: "men", clothingSubtype: "tshirt", name: "Sports Tee", price: 1400, color: "Red", dateScraped: "2024-01-19" },
  { id: "19", competitor: "coolplanet", clothingType: "women", clothingSubtype: "tshirt", name: "Basic Tee", price: 1300, color: "Grey", dateScraped: "2024-01-20" },
  { id: "20", competitor: "coolplanet", clothingType: "women", clothingSubtype: "jean", name: "Skinny Jeans", price: 3300, color: "Black", dateScraped: "2024-01-20" },
  
  { id: "21", competitor: "fashionbug", clothingType: "men", clothingSubtype: "shirt", name: "Oxford Shirt", price: 2900, color: "Blue", dateScraped: "2024-01-21" },
  { id: "22", competitor: "fashionbug", clothingType: "women", clothingSubtype: "skirt", name: "Pleated Skirt", price: 2100, color: "Blue", dateScraped: "2024-01-21" },
  { id: "23", competitor: "coolplanet", clothingType: "men", clothingSubtype: "trouser", name: "Slim Trousers", price: 2700, color: "Black", dateScraped: "2024-01-22" },
  { id: "24", competitor: "coolplanet", clothingType: "women", clothingSubtype: "saree", name: "Cotton Saree", price: 3800, color: "Red", dateScraped: "2024-01-22" },
];

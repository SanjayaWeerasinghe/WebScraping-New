/**
 * API service for fetching data from the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ScrapedItem {
  id: string;
  competitor: "fashionbug" | "coolplanet";
  clothingType: "men" | "women";
  clothingSubtype: string;
  name: string;
  price: number;
  colors: string[];  // Array of colors
  imageUrl?: string;  // Product image URL
  dateScraped: string;
}

export interface PaginatedResponse {
  items: ScrapedItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface FilterOptions {
  competitors: string[];
  clothing_types: string[];
  clothing_subtypes: string[];
}

export interface PriceHistoryItem {
  product_id: number;
  product_name: string;
  product_url: string;
  site: string;
  prices: Array<{
    date: string;
    price: string;
    price_numeric: number;
  }>;
}

export interface ColorTrendItem {
  color: string;
  count: number;
  site: string;
  clothing_type: string;
}

export interface StatsResponse {
  total_products: number;
  total_sessions: number;
  sites: Record<string, number>;
  price_range: {
    min: number;
    max: number;
    avg: number;
  };
}

export interface PriceTrendItem {
  date: string;
  site: string;
  gender: string;
  avg_price: number;
  min_price: number;
  max_price: number;
  product_count: number;
}

export interface ProductTimelineItem {
  date: string;
  total: number;
  "FashionBug Men"?: number;
  "FashionBug Women"?: number;
  "CoolPlanet Men"?: number;
  "CoolPlanet Women"?: number;
}

export interface ColorPriceTrendItem {
  date: string;
  Black?: number;
  White?: number;
  Gray?: number;
  Red?: number;
  Blue?: number;
  Green?: number;
  Yellow?: number;
  Orange?: number;
  Purple?: number;
  Pink?: number;
  Brown?: number;
  Other?: number;
  [key: string]: number | string | undefined;
}

/**
 * Fetch all products with optional filters and pagination
 */
export async function fetchProducts(params?: {
  site?: string;
  gender?: string;
  clothing_type?: string;
  page?: number;
  page_size?: number;
  start_date?: string;
  end_date?: string;
}): Promise<PaginatedResponse> {
  const queryParams = new URLSearchParams();

  if (params?.site) queryParams.append('site', params.site);
  if (params?.gender) queryParams.append('gender', params.gender);
  if (params?.clothing_type) queryParams.append('clothing_type', params.clothing_type);
  if (params?.page) queryParams.append('page', params.page.toString());
  if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
  if (params?.start_date) queryParams.append('start_date', params.start_date);
  if (params?.end_date) queryParams.append('end_date', params.end_date);

  const url = `${API_BASE_URL}/api/products${queryParams.toString() ? `?${queryParams}` : ''}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch products: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch available filter options based on actual data
 */
export async function fetchFilterOptions(): Promise<FilterOptions> {
  const response = await fetch(`${API_BASE_URL}/api/filter-options`);

  if (!response.ok) {
    throw new Error(`Failed to fetch filter options: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch price history for a specific product
 */
export async function fetchPriceHistory(productId: number): Promise<PriceHistoryItem> {
  const response = await fetch(`${API_BASE_URL}/api/price-history/${productId}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch price history: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch color trends with optional site filter
 */
export async function fetchColorTrends(site?: string): Promise<ColorTrendItem[]> {
  const url = site
    ? `${API_BASE_URL}/api/color-trends?site=${site}`
    : `${API_BASE_URL}/api/color-trends`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch color trends: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch database statistics
 */
export async function fetchStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/stats`);

  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch price trends over time with optional filters
 */
export async function fetchPriceTrends(params?: {
  site?: string;
  gender?: string;
  clothing_type?: string;
  start_date?: string;
  end_date?: string;
}): Promise<PriceTrendItem[]> {
  const queryParams = new URLSearchParams();

  if (params?.site) queryParams.append('site', params.site);
  if (params?.gender) queryParams.append('gender', params.gender);
  if (params?.clothing_type) queryParams.append('clothing_type', params.clothing_type);
  if (params?.start_date) queryParams.append('start_date', params.start_date);
  if (params?.end_date) queryParams.append('end_date', params.end_date);

  const url = `${API_BASE_URL}/api/price-trends${queryParams.toString() ? `?${queryParams}` : ''}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch price trends: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch product launch timeline with optional filters
 */
export async function fetchProductTimeline(params?: {
  site?: string;
  gender?: string;
  clothing_type?: string;
}): Promise<ProductTimelineItem[]> {
  const queryParams = new URLSearchParams();

  if (params?.site) queryParams.append('site', params.site);
  if (params?.gender) queryParams.append('gender', params.gender);
  if (params?.clothing_type) queryParams.append('clothing_type', params.clothing_type);

  const url = `${API_BASE_URL}/api/product-timeline${queryParams.toString() ? `?${queryParams}` : ''}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch product timeline: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch color price trends over time
 */
export async function fetchColorPriceTrends(params?: {
  site?: string;
  gender?: string;
  start_date?: string;
  end_date?: string;
}): Promise<ColorPriceTrendItem[]> {
  const queryParams = new URLSearchParams();

  if (params?.site) queryParams.append('site', params.site);
  if (params?.gender) queryParams.append('gender', params.gender);
  if (params?.start_date) queryParams.append('start_date', params.start_date);
  if (params?.end_date) queryParams.append('end_date', params.end_date);

  const url = `${API_BASE_URL}/api/color-price-trends${queryParams.toString() ? `?${queryParams}` : ''}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch color price trends: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check if API is available
 */
export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/`);
    return response.ok;
  } catch {
    return false;
  }
}

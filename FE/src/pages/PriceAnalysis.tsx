import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FilterBar, Filters } from "@/components/FilterBar";
import { fetchProducts, fetchFilterOptions, fetchPriceTrends } from "@/services/api";
import { filterData } from "@/utils/filterData";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, ComposedChart, Area, BarChart, Bar, Cell } from "recharts";

const PriceAnalysis = () => {
  const [filters, setFilters] = useState<Filters>({
    competitor: "all",
    clothingType: "all",
    clothingSubtype: "all",
    startDate: "",
    endDate: "",
  });

  // Fetch filter options
  const { data: filterOptions } = useQuery({
    queryKey: ['filter-options'],
    queryFn: fetchFilterOptions,
  });

  // Fetch ALL products from API for analysis (no pagination)
  const { data: productsData, isLoading, error } = useQuery({
    queryKey: ['products-analysis'],
    queryFn: () => fetchProducts({ page: 1, page_size: 10000 }),
  });

  // Fetch price trends data
  const { data: priceTrendsData } = useQuery({
    queryKey: ['price-trends', filters],
    queryFn: () => fetchPriceTrends({
      site: filters.competitor !== "all" ? filters.competitor : undefined,
      gender: filters.clothingType !== "all" ? filters.clothingType : undefined,
      clothing_type: filters.clothingSubtype !== "all" ? filters.clothingSubtype : undefined,
      start_date: filters.startDate || undefined,
      end_date: filters.endDate || undefined,
    }),
  });

  const products = productsData?.items || [];
  const priceTrends = priceTrendsData || [];

  const handleFilterChange = (key: keyof Filters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  if (isLoading) {
    return (
      <div className="min-h-screen py-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading products...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen py-8 flex items-center justify-center">
        <div className="text-center text-destructive">
          <p className="text-xl font-semibold">Error loading products</p>
          <p className="text-sm mt-2">{error instanceof Error ? error.message : 'Unknown error'}</p>
          <p className="text-sm mt-2 text-muted-foreground">Make sure the API server is running on port 8000</p>
        </div>
      </div>
    );
  }

  const filteredData = filterData(products || [], filters);

  // Calculate market share by category
  const marketShareByCategory = products.reduce((acc, product) => {
    const category = product.clothingSubtype || "Unknown";

    if (!acc[category]) {
      acc[category] = {
        category,
        fashionbug: 0,
        coolplanet: 0,
        total: 0,
      };
    }

    if (product.competitor === "fashionbug") {
      acc[category].fashionbug += 1;
    } else if (product.competitor === "coolplanet") {
      acc[category].coolplanet += 1;
    }
    acc[category].total += 1;

    return acc;
  }, {} as Record<string, any>);

  const marketShareData = Object.values(marketShareByCategory).map((cat: any) => ({
    category: cat.category,
    fashionbug_count: cat.fashionbug,
    coolplanet_count: cat.coolplanet,
    fashionbug_percent: ((cat.fashionbug / cat.total) * 100).toFixed(1),
    coolplanet_percent: ((cat.coolplanet / cat.total) * 100).toFixed(1),
    total: cat.total,
  })).sort((a, b) => b.total - a.total).slice(0, 10); // Top 10 categories

  // Transform price trends data for line chart
  // Group by date and create separate series for each site/gender combination
  const trendsByDate = priceTrends.reduce((acc, trend) => {
    const siteName = trend.site === "fashionbug" ? "FashionBug" : trend.site === "coolplanet" ? "CoolPlanet" : trend.site;
    const genderCapitalized = trend.gender.charAt(0).toUpperCase() + trend.gender.slice(1);
    const seriesKey = `${siteName} ${genderCapitalized}`;

    if (!acc[trend.date]) {
      acc[trend.date] = { date: trend.date };
    }
    acc[trend.date][seriesKey] = trend.avg_price;
    acc[trend.date][`${seriesKey}_min`] = trend.min_price;
    acc[trend.date][`${seriesKey}_max`] = trend.max_price;

    return acc;
  }, {} as Record<string, any>);

  const priceTrendsChartData = Object.values(trendsByDate).sort((a: any, b: any) =>
    new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  // Get unique series names for the legend
  const seriesNames = Array.from(new Set(priceTrends.map(t => {
    const siteName = t.site === "fashionbug" ? "FashionBug" : t.site === "coolplanet" ? "CoolPlanet" : t.site;
    const genderCapitalized = t.gender.charAt(0).toUpperCase() + t.gender.slice(1);
    return `${siteName} ${genderCapitalized}`;
  })));

  // Prepare price distribution data (showing range for each series)
  const priceDistributionData = priceTrends.map(t => ({
    date: t.date,
    site: t.site === "fashionbug" ? "FashionBug" : "CoolPlanet",
    gender: t.gender.charAt(0).toUpperCase() + t.gender.slice(1),
    series: `${t.site === "fashionbug" ? "FashionBug" : "CoolPlanet"} ${t.gender.charAt(0).toUpperCase() + t.gender.slice(1)}`,
    avg_price: t.avg_price,
    min_price: t.min_price,
    max_price: t.max_price,
    range: t.max_price - t.min_price,
  })).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  // Calculate price gaps between competitors
  const priceGapsByDate = priceTrends.reduce((acc, trend) => {
    const gender = trend.gender.charAt(0).toUpperCase() + trend.gender.slice(1);
    const site = trend.site === "fashionbug" ? "fashionbug" : "coolplanet";

    if (!acc[trend.date]) {
      acc[trend.date] = { date: trend.date };
    }

    if (!acc[trend.date][gender]) {
      acc[trend.date][gender] = {};
    }

    acc[trend.date][gender][site] = trend.avg_price;

    return acc;
  }, {} as Record<string, any>);

  const priceGapData = Object.values(priceGapsByDate).map((dateData: any) => {
    const result: any = { date: dateData.date };

    // Calculate gaps for each gender
    ['Men', 'Women'].forEach(gender => {
      if (dateData[gender]?.fashionbug !== undefined && dateData[gender]?.coolplanet !== undefined) {
        const gap = dateData[gender].coolplanet - dateData[gender].fashionbug;
        result[`${gender}_Gap`] = gap;
        result[`${gender}_FashionBug`] = dateData[gender].fashionbug;
        result[`${gender}_CoolPlanet`] = dateData[gender].coolplanet;
      }
    });

    return result;
  }).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  // Price vs Clothing Type - Combined with Competitor
  // Creates categories like "FashionBug Men", "CoolPlanet Women", etc.
  const priceByTypeWithCompetitor = filteredData.map((item) => {
    const competitorName = item.competitor === "fashionbug" ? "FashionBug" : "CoolPlanet";
    const typeName = item.clothingType.charAt(0).toUpperCase() + item.clothingType.slice(1); // Capitalize
    const combinedCategory = `${competitorName} ${typeName}`;

    return {
      category: combinedCategory,
      price: item.price,
      name: item.name,
      competitor: item.competitor,
    };
  });

  // Price vs Clothing Subtype with Competitor and Gender
  const priceBySubtypeWithCompetitor = filteredData.map((item) => {
    const competitorName = item.competitor === "fashionbug" ? "FashionBug" : "CoolPlanet";
    const typeName = item.clothingType.charAt(0).toUpperCase() + item.clothingType.slice(1);
    const subtypeName = item.clothingSubtype.charAt(0).toUpperCase() + item.clothingSubtype.slice(1);
    const combinedCategory = `${competitorName} ${typeName} ${subtypeName}`;

    return {
      category: combinedCategory,
      price: item.price,
      name: item.name,
      competitor: item.competitor,
    };
  });

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 space-y-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Price Analysis</h1>
          <p className="text-muted-foreground text-lg">
            Compare pricing strategies across competitors and product categories
          </p>
        </div>

        <FilterBar filters={filters} onFilterChange={handleFilterChange} filterOptions={filterOptions} />

        <div className="grid gap-8">
          {/* Price Trends Over Time */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Price Trends Over Time</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Average price changes across different scraping sessions
            </p>
            {priceTrendsChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={priceTrendsChartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis
                    dataKey="date"
                    className="text-sm"
                    label={{ value: 'Date', position: 'insideBottom', offset: -10 }}
                  />
                  <YAxis
                    className="text-sm"
                    label={{ value: 'Average Price (Rs)', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-background border border-border rounded-lg shadow-lg p-3">
                            <p className="font-semibold mb-2">{payload[0].payload.date}</p>
                            {payload.map((entry, index) => (
                              <p key={index} className="text-sm" style={{ color: entry.color }}>
                                {entry.name}: Rs {entry.value?.toLocaleString()}
                              </p>
                            ))}
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Legend />
                  {seriesNames.includes("FashionBug Men") && (
                    <Line
                      type="monotone"
                      dataKey="FashionBug Men"
                      stroke="#8884d8"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  )}
                  {seriesNames.includes("FashionBug Women") && (
                    <Line
                      type="monotone"
                      dataKey="FashionBug Women"
                      stroke="#82ca9d"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  )}
                  {seriesNames.includes("CoolPlanet Men") && (
                    <Line
                      type="monotone"
                      dataKey="CoolPlanet Men"
                      stroke="#ffc658"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  )}
                  {seriesNames.includes("CoolPlanet Women") && (
                    <Line
                      type="monotone"
                      dataKey="CoolPlanet Women"
                      stroke="#ff7c7c"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  )}
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <p className="text-lg font-medium">No time-series data available yet</p>
                <p className="text-sm mt-2">
                  Price trends will appear here once you run the scraper multiple times.
                  <br />
                  Currently showing data from only 1 scraping session.
                </p>
              </div>
            )}
          </div>

          {/* Price Distribution Over Time */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Price Distribution Over Time</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Price ranges (min-max) and average prices across different categories
            </p>
            {priceDistributionData.length > 0 ? (
              <div className="space-y-8">
                {seriesNames.map((seriesName, index) => {
                  const seriesData = priceDistributionData.filter(d => d.series === seriesName);
                  if (seriesData.length === 0) return null;

                  const colors = ["#8884d8", "#82ca9d", "#ffc658", "#ff7c7c"];
                  const color = colors[index % colors.length];

                  return (
                    <div key={seriesName}>
                      <h4 className="text-sm font-medium mb-3">{seriesName}</h4>
                      <ResponsiveContainer width="100%" height={250}>
                        <ComposedChart data={seriesData} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
                          <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                          <XAxis
                            dataKey="date"
                            className="text-xs"
                            tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                          />
                          <YAxis
                            className="text-xs"
                            label={{ value: 'Price (Rs)', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }}
                          />
                          <Tooltip
                            content={({ active, payload }) => {
                              if (active && payload && payload.length) {
                                const data = payload[0].payload;
                                return (
                                  <div className="bg-background border border-border rounded-lg shadow-lg p-3">
                                    <p className="font-semibold text-sm mb-1">{data.date}</p>
                                    <p className="text-xs text-muted-foreground">Max: Rs {data.max_price?.toLocaleString()}</p>
                                    <p className="text-xs font-medium">Avg: Rs {data.avg_price?.toLocaleString()}</p>
                                    <p className="text-xs text-muted-foreground">Min: Rs {data.min_price?.toLocaleString()}</p>
                                    <p className="text-xs text-muted-foreground mt-1">Range: Rs {data.range?.toLocaleString()}</p>
                                  </div>
                                );
                              }
                              return null;
                            }}
                          />
                          <Area
                            type="monotone"
                            dataKey="max_price"
                            stroke="none"
                            fill={color}
                            fillOpacity={0.1}
                            name="Max"
                          />
                          <Area
                            type="monotone"
                            dataKey="min_price"
                            stroke="none"
                            fill="#ffffff"
                            fillOpacity={1}
                            name="Min"
                          />
                          <Line
                            type="monotone"
                            dataKey="avg_price"
                            stroke={color}
                            strokeWidth={2}
                            dot={{ r: 3 }}
                            name="Average"
                          />
                          <Line
                            type="monotone"
                            dataKey="max_price"
                            stroke={color}
                            strokeWidth={1}
                            strokeDasharray="3 3"
                            dot={false}
                            name="Max"
                            opacity={0.5}
                          />
                          <Line
                            type="monotone"
                            dataKey="min_price"
                            stroke={color}
                            strokeWidth={1}
                            strokeDasharray="3 3"
                            dot={false}
                            name="Min"
                            opacity={0.5}
                          />
                        </ComposedChart>
                      </ResponsiveContainer>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <p className="text-lg font-medium">No price distribution data available</p>
                <p className="text-sm mt-2">
                  Price ranges will appear here as more data is collected.
                </p>
              </div>
            )}
          </div>

          {/* Price Gap Analysis */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Competitive Price Gap Analysis</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Average price difference between CoolPlanet and FashionBug over time
              <span className="block mt-1 text-xs">Positive values mean CoolPlanet is more expensive, negative means FashionBug is more expensive</span>
            </p>
            {priceGapData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <ComposedChart data={priceGapData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis
                    dataKey="date"
                    className="text-sm"
                    tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis
                    className="text-sm"
                    label={{ value: 'Price Gap (Rs)', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-background border border-border rounded-lg shadow-lg p-3">
                            <p className="font-semibold text-sm mb-2">{data.date}</p>
                            {data.Men_Gap !== undefined && (
                              <div className="mb-2">
                                <p className="text-xs font-medium">Men's Category:</p>
                                <p className="text-xs text-muted-foreground">CoolPlanet: Rs {data.Men_CoolPlanet?.toLocaleString()}</p>
                                <p className="text-xs text-muted-foreground">FashionBug: Rs {data.Men_FashionBug?.toLocaleString()}</p>
                                <p className={`text-xs font-medium ${data.Men_Gap >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                                  Gap: Rs {data.Men_Gap?.toLocaleString()} {data.Men_Gap >= 0 ? '(CP higher)' : '(FB higher)'}
                                </p>
                              </div>
                            )}
                            {data.Women_Gap !== undefined && (
                              <div>
                                <p className="text-xs font-medium">Women's Category:</p>
                                <p className="text-xs text-muted-foreground">CoolPlanet: Rs {data.Women_CoolPlanet?.toLocaleString()}</p>
                                <p className="text-xs text-muted-foreground">FashionBug: Rs {data.Women_FashionBug?.toLocaleString()}</p>
                                <p className={`text-xs font-medium ${data.Women_Gap >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                                  Gap: Rs {data.Women_Gap?.toLocaleString()} {data.Women_Gap >= 0 ? '(CP higher)' : '(FB higher)'}
                                </p>
                              </div>
                            )}
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Legend />
                  {/* Reference line at 0 */}
                  <Line
                    type="monotone"
                    dataKey={() => 0}
                    stroke="#666"
                    strokeWidth={1}
                    strokeDasharray="5 5"
                    dot={false}
                    name="Equal Price"
                  />
                  {/* Men's gap */}
                  <Area
                    type="monotone"
                    dataKey="Men_Gap"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.3}
                    name="Men's Gap"
                  />
                  {/* Women's gap */}
                  <Area
                    type="monotone"
                    dataKey="Women_Gap"
                    stroke="#82ca9d"
                    fill="#82ca9d"
                    fillOpacity={0.3}
                    name="Women's Gap"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <p className="text-lg font-medium">No price gap data available</p>
                <p className="text-sm mt-2">
                  Price comparisons will appear here as more data is collected.
                </p>
              </div>
            )}
          </div>

          {/* Market Share by Category */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Market Share by Product Category</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Percentage distribution of products by category for each competitor (Top 10 categories by total products)
            </p>
            {marketShareData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={marketShareData} layout="vertical" margin={{ top: 20, right: 100, left: 100, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis
                    type="number"
                    className="text-sm"
                    label={{ value: 'Percentage (%)', position: 'insideBottom', offset: -10 }}
                    domain={[0, 100]}
                  />
                  <YAxis
                    type="category"
                    dataKey="category"
                    className="text-sm"
                    width={90}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-background border border-border rounded-lg shadow-lg p-3">
                            <p className="font-semibold text-sm mb-2">{data.category}</p>
                            <p className="text-xs mb-1">Total Products: {data.total}</p>
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#8884d8' }}></div>
                                <p className="text-xs">
                                  FashionBug: {data.fashionbug_count} ({data.fashionbug_percent}%)
                                </p>
                              </div>
                              <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#82ca9d' }}></div>
                                <p className="text-xs">
                                  CoolPlanet: {data.coolplanet_count} ({data.coolplanet_percent}%)
                                </p>
                              </div>
                            </div>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Legend />
                  <Bar
                    dataKey="fashionbug_percent"
                    stackId="stack"
                    fill="#8884d8"
                    name="FashionBug"
                  />
                  <Bar
                    dataKey="coolplanet_percent"
                    stackId="stack"
                    fill="#82ca9d"
                    name="CoolPlanet"
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <p className="text-lg font-medium">No market share data available</p>
                <p className="text-sm mt-2">
                  Market share analysis will appear here once product data is available.
                </p>
              </div>
            )}
          </div>

          {/* Price vs Clothing Type by Competitor */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Price vs Clothing Type by Competitor</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Each dot represents one product. Categories combine competitor and gender.
            </p>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis
                  type="category"
                  dataKey="category"
                  name="Category"
                  className="text-sm"
                  allowDuplicatedCategory={false}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis
                  type="number"
                  dataKey="price"
                  name="Price (Rs)"
                  className="text-sm"
                  label={{ value: 'Price (Rs)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-background border border-border rounded-lg shadow-lg p-3">
                          <p className="font-semibold">{data.name}</p>
                          <p className="text-sm text-muted-foreground">{data.category}</p>
                          <p className="text-sm font-medium">Rs {data.price?.toLocaleString()}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter
                  name="Products"
                  data={priceByTypeWithCompetitor}
                  fill="hsl(var(--primary))"
                  fillOpacity={0.6}
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          {/* Price vs Clothing Subtype by Competitor */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Price vs Clothing Subtype by Competitor & Gender</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Each dot represents one product. Categories combine competitor, gender, and product type (e.g., FashionBug Men T-Shirt).
            </p>
            <ResponsiveContainer width="100%" height={500}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 120, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis
                  type="category"
                  dataKey="category"
                  name="Category"
                  className="text-sm"
                  allowDuplicatedCategory={false}
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  interval={0}
                />
                <YAxis
                  type="number"
                  dataKey="price"
                  name="Price (Rs)"
                  className="text-sm"
                  label={{ value: 'Price (Rs)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-background border border-border rounded-lg shadow-lg p-3">
                          <p className="font-semibold">{data.name}</p>
                          <p className="text-sm text-muted-foreground">{data.category}</p>
                          <p className="text-sm font-medium">Rs {data.price?.toLocaleString()}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter
                  name="Products"
                  data={priceBySubtypeWithCompetitor}
                  fill="hsl(var(--accent))"
                  fillOpacity={0.6}
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PriceAnalysis;

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FilterBar, Filters } from "@/components/FilterBar";
import { fetchProducts, fetchFilterOptions } from "@/services/api";
import { filterData } from "@/utils/filterData";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from "recharts";

// Categorize specific color shades into base color groups
const categorizeColor = (colorName: string): string => {
  if (!colorName) return "Other";

  const color = colorName.toLowerCase();

  // Black shades (check first to avoid false matches with "blue-black" etc)
  if (color.includes("black") || color.includes("ebony") || color.includes("onyx") ||
      color.includes("jet") || color.includes("noir") || color.includes("charcoal") ||
      color.includes("eerie") || color.includes("raisin") || color.includes("smoky")) {
    return "Black";
  }

  // White shades
  if (color.includes("white") || color.includes("ivory") || color.includes("cream") ||
      color.includes("alabaster") || color.includes("pearl") || color.includes("cultured") ||
      color.includes("magnolia") || color.includes("vanilla") || color.includes("bone") ||
      color.includes("isabelline") || color.includes("ghost")) {
    return "White";
  }

  // Gray shades
  if (color.includes("gray") || color.includes("grey") || color.includes("silver") ||
      color.includes("slate") || color.includes("ash") || color.includes("dim gray") ||
      color.includes("gunmetal") || color.includes("nickel") || color.includes("platinum") ||
      color.includes("gainsboro") || color.includes("manatee") || color.includes("quick silver") ||
      color.includes("sonic silver") || color.includes("roman silver") || color.includes("davy") ||
      color.includes("payne") || color.includes("feldgrau") || color.includes("cadet grey") ||
      color.includes("spanish gray") || color.includes("granite") || color.includes("cinereous") ||
      color.includes("grullo")) {
    return "Gray";
  }

  // Red shades
  if (color.includes("red") || color.includes("maroon") || color.includes("crimson") ||
      color.includes("scarlet") || color.includes("burgundy") || color.includes("wine") ||
      color.includes("cardinal") || color.includes("carmine") || color.includes("claret") ||
      color.includes("ruby") || color.includes("brick") || color.includes("cordovan") ||
      color.includes("vermillion") || color.includes("madder") || color.includes("upsdell")) {
    return "Red";
  }

  // Blue shades
  if (color.includes("blue") || color.includes("navy") || color.includes("azure") ||
      color.includes("cobalt") || color.includes("sapphire") || color.includes("indigo") ||
      color.includes("cerulean") || color.includes("periwinkle") || color.includes("cornflower") ||
      color.includes("teal") || color.includes("prussian") || color.includes("denim") ||
      color.includes("han blue") || color.includes("yinmn") || color.includes("oxford") ||
      color.includes("cadet blue") || color.includes("alice") || color.includes("space cadet") ||
      color.includes("queen blue") || color.includes("morning blue") || color.includes("powder blue")) {
    return "Blue";
  }

  // Green shades
  if (color.includes("green") || color.includes("olive") || color.includes("lime") ||
      color.includes("emerald") || color.includes("mint") || color.includes("sage") ||
      color.includes("jungle") || color.includes("viridian") || color.includes("shamrock") ||
      color.includes("hooker") || color.includes("phthalo") || color.includes("kombu") ||
      color.includes("castleton") || color.includes("rifle") || color.includes("pine") ||
      color.includes("sacramento") || color.includes("msu green") || color.includes("russian green") ||
      color.includes("english green") || color.includes("artichoke") || color.includes("laurel") ||
      color.includes("charleston") || color.includes("zomp")) {
    return "Green";
  }

  // Yellow shades
  if (color.includes("yellow") || color.includes("gold") || color.includes("mustard") ||
      color.includes("amber") || color.includes("lemon") || color.includes("jonquil") ||
      color.includes("maize") || color.includes("hansa") || color.includes("earth yellow") ||
      color.includes("harvest") || color.includes("sunray")) {
    return "Yellow";
  }

  // Orange shades
  if (color.includes("orange") || color.includes("coral") || color.includes("peach") ||
      color.includes("tangerine") || color.includes("apricot") || color.includes("melon") ||
      color.includes("persian orange") || color.includes("copper")) {
    return "Orange";
  }

  // Purple/Violet shades
  if (color.includes("purple") || color.includes("violet") || color.includes("lavender") ||
      color.includes("mauve") || color.includes("plum") || color.includes("lilac") ||
      color.includes("eggplant") || color.includes("byzantium") || color.includes("grape") ||
      color.includes("mulberry") || color.includes("thistle") || color.includes("languid") ||
      color.includes("cyber grape") || color.includes("independence") || color.includes("prune") ||
      color.includes("puce")) {
    return "Purple";
  }

  // Pink shades
  if (color.includes("pink") || color.includes("rose") || color.includes("fuchsia") ||
      color.includes("magenta") || color.includes("blush") || color.includes("cameo") ||
      color.includes("charm") || color.includes("champagne") || color.includes("cyclamen") ||
      color.includes("mountbatten") || color.includes("nadeshiko") || color.includes("pastel") ||
      color.includes("queen pink") || color.includes("raspberry") || color.includes("sherbet") ||
      color.includes("tango pink") || color.includes("quinacridone") || color.includes("shimmering")) {
    return "Pink";
  }

  // Brown shades
  if (color.includes("brown") || color.includes("tan") || color.includes("beige") ||
      color.includes("khaki") || color.includes("taupe") || color.includes("camel") ||
      color.includes("chocolate") || color.includes("coffee") || color.includes("sienna") ||
      color.includes("umber") || color.includes("sepia") || color.includes("bistre") ||
      color.includes("bronze") || color.includes("brass") || color.includes("burnished") ||
      color.includes("liver") || color.includes("beaver") || color.includes("bole") ||
      color.includes("brandy") || color.includes("buff") || color.includes("burnt") ||
      color.includes("caf�") || color.includes("caput") || color.includes("chestnut") ||
      color.includes("coyote") || color.includes("fawn") || color.includes("kobicha") ||
      color.includes("sand") || color.includes("tumbleweed") || color.includes("tuscan") ||
      color.includes("wood") || color.includes("van dyke") || color.includes("redwood") ||
      color.includes("opal") || color.includes("desert") || color.includes("almond") ||
      color.includes("auburn") || color.includes("deer")) {
    return "Brown";
  }

  // Multi-color
  if (color.includes("multi") || color.includes("print") || color.includes("pattern") ||
      color.includes("mix") || color.includes("assorted")) {
    return "Multicolor";
  }

  // If no match, return "Other"
  return "Other";
};

const ColorTrends = () => {
  const [filters, setFilters] = useState<Filters>({
    competitor: "all",
    clothingType: "all",
    clothingSubtype: "all",
  });

  // Fetch filter options
  const { data: filterOptions } = useQuery({
    queryKey: ['filter-options'],
    queryFn: fetchFilterOptions,
  });

  // Fetch ALL products from API for analysis (no pagination)
  const { data: productsData, isLoading, error } = useQuery({
    queryKey: ['products-color-trends'],
    queryFn: () => fetchProducts({ page: 1, page_size: 10000 }),
  });

  const handleFilterChange = (key: keyof Filters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Use appropriate color based on product type and competitor
  // For FashionBug tops (T-Shirt, Shirt, Blouse, Top), use 2nd color as 1st might be from pants in the photo
  // For CoolPlanet and other items, use 1st color
  const allProducts = productsData?.items || [];
  const productsWithTopColor = allProducts.map(product => {
    const isFashionBug = product.competitor === "fashionbug";
    const isTopItem = product.clothingSubtype &&
      (product.clothingSubtype.toLowerCase().includes('shirt') ||
       product.clothingSubtype.toLowerCase().includes('blouse') ||
       product.clothingSubtype.toLowerCase().includes('top'));

    // Use 2nd color for FashionBug tops (if available), 1st color for everything else
    const colorIndex = isFashionBug && isTopItem && product.colors.length > 1 ? 1 : 0;
    const selectedColor = product.colors[colorIndex] || product.colors[0] || "Unknown";

    return {
      id: product.id,
      competitor: product.competitor,
      clothingType: product.clothingType,
      clothingSubtype: product.clothingSubtype,
      name: product.name,
      price: product.price,
      color: categorizeColor(selectedColor), // Categorize to base color
      originalColor: selectedColor, // Keep original for tooltip
      dateScraped: product.dateScraped,
    };
  });

  const filteredData = filterData(productsWithTopColor, filters);

  // Create category mappings
  const typeMapping = { 'men': 0, 'women': 1 };
  const subtypeMapping = { 'shirt': 0, 'tshirt': 1, 'skirt': 2, 'jean': 3, 'trouser': 4, 'saree': 5, 'frock': 6 };
  
  // Get unique colors and create mapping
  const uniqueColors = Array.from(new Set(filteredData.map(item => item.color)));
  const colorMapping = Object.fromEntries(uniqueColors.map((color, index) => [color, index]));

  // Color vs Clothing Type - each item gets its own dot
  const colorByType = filteredData.map((item) => ({
    typeValue: typeMapping[item.clothingType],
    typeName: item.clothingType,
    colorValue: colorMapping[item.color],
    colorName: item.color,
    name: item.name,
  }));

  // Color vs Clothing Subtype - each item gets its own dot
  const colorBySubtype = filteredData.map((item) => ({
    subtypeValue: subtypeMapping[item.clothingSubtype],
    subtypeName: item.clothingSubtype,
    colorValue: colorMapping[item.color],
    colorName: item.color,
    name: item.name,
  }));

  // Color vs Competitor Type
  const fashionbugColorType = filteredData
    .filter(item => item.competitor === "fashionbug")
    .map((item) => ({ 
      typeValue: typeMapping[item.clothingType],
      typeName: item.clothingType,
      colorValue: colorMapping[item.color],
      colorName: item.color,
      name: item.name,
    }));
  
  const coolplanetColorType = filteredData
    .filter(item => item.competitor === "coolplanet")
    .map((item) => ({ 
      typeValue: typeMapping[item.clothingType],
      typeName: item.clothingType,
      colorValue: colorMapping[item.color],
      colorName: item.color,
      name: item.name,
    }));

  // Color vs Competitor Subtype
  const fashionbugColorSubtype = filteredData
    .filter(item => item.competitor === "fashionbug")
    .map((item) => ({ 
      subtypeValue: subtypeMapping[item.clothingSubtype],
      subtypeName: item.clothingSubtype,
      colorValue: colorMapping[item.color],
      colorName: item.color,
      name: item.name,
    }));
  
  const coolplanetColorSubtype = filteredData
    .filter(item => item.competitor === "coolplanet")
    .map((item) => ({ 
      subtypeValue: subtypeMapping[item.clothingSubtype],
      subtypeName: item.clothingSubtype,
      colorValue: colorMapping[item.color],
      colorName: item.color,
      name: item.name,
    }));

  // Color Distribution Pie Chart
  const colorCounts = filteredData.reduce((acc, item) => {
    acc[item.color] = (acc[item.color] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const pieData = Object.entries(colorCounts).map(([name, value]) => ({
    name,
    value,
  }));

  // Detailed color breakdown by competitor (using original color names)
  const detailedColorCounts: Record<string, { fashionbug: number; coolplanet: number }> = {};
  filteredData.forEach(item => {
    const originalColor = item.originalColor;
    if (!detailedColorCounts[originalColor]) {
      detailedColorCounts[originalColor] = { fashionbug: 0, coolplanet: 0 };
    }
    if (item.competitor === "fashionbug") {
      detailedColorCounts[originalColor].fashionbug += 1;
    } else {
      detailedColorCounts[originalColor].coolplanet += 1;
    }
  });

  // Convert to bar chart format and sort by total count
  const detailedColorData = Object.entries(detailedColorCounts)
    .map(([color, counts]) => ({
      color,
      fashionbug: counts.fashionbug,
      coolplanet: counts.coolplanet,
      total: counts.fashionbug + counts.coolplanet,
    }))
    .sort((a, b) => b.total - a.total); // Sort by total descending

  // Map color categories to actual hex colors
  const COLOR_MAP: Record<string, string> = {
    "Red": "#DC2626",
    "Blue": "#2563EB",
    "Green": "#16A34A",
    "Yellow": "#FACC15",
    "Orange": "#F97316",
    "Purple": "#9333EA",
    "Pink": "#EC4899",
    "Brown": "#92400E",
    "Black": "#000000",
    "White": "#FFFFFF",
    "Gray": "#6B7280",
    "Multicolor": "linear-gradient(90deg, #DC2626, #F97316, #FACC15, #16A34A, #2563EB, #9333EA)",
    "Other": "#A8A29E",
  };

  // Get color for pie chart slice
  const getSliceColor = (colorName: string): string => {
    return COLOR_MAP[colorName] || "#A8A29E";
  };

  // Custom tick formatters
  const typeTickFormatter = (value: number) => {
    return value === 0 ? 'Men' : 'Women';
  };

  const subtypeTickFormatter = (value: number) => {
    const subtypes = ['Shirt', 'T-Shirt', 'Skirt', 'Jean', 'Trouser', 'Saree', 'Frock'];
    return subtypes[value] || '';
  };

  const colorTickFormatter = (value: number) => {
    return uniqueColors[value] || '';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen py-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading color trends...</p>
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

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 space-y-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Color Trends</h1>
          <p className="text-muted-foreground text-lg">
            Analyze color preferences and trends across product categories
          </p>
        </div>

        <FilterBar filters={filters} onFilterChange={handleFilterChange} filterOptions={filterOptions} />

        <div className="grid gap-8">
          {/* Most Used Colors Pie Chart */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Most Used Colors</h3>
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={120}
                  fill="hsl(var(--primary))"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={getSliceColor(entry.name)}
                      stroke={entry.name === "White" ? "#D1D5DB" : undefined}
                      strokeWidth={entry.name === "White" ? 2 : undefined}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Detailed Color Breakdown by Competitor */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Detailed Color Breakdown by Competitor</h3>
            <p className="text-sm text-muted-foreground mb-4">
              All {detailedColorData.length} unique color shades sorted by popularity. Each color shows quantity from both competitors.
            </p>
            <ResponsiveContainer width="100%" height={Math.max(600, detailedColorData.length * 25)}>
              <BarChart
                data={detailedColorData}
                layout="vertical"
                margin={{ top: 20, right: 30, left: 150, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis type="number" className="text-sm" label={{ value: 'Quantity', position: 'bottom' }} />
                <YAxis
                  type="category"
                  dataKey="color"
                  className="text-xs"
                  width={140}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-background border border-border rounded-lg shadow-lg p-3">
                          <p className="font-semibold text-sm">{data.color}</p>
                          <p className="text-xs text-primary">FashionBug: {data.fashionbug}</p>
                          <p className="text-xs text-accent">CoolPlanet: {data.coolplanet}</p>
                          <p className="text-xs font-medium mt-1">Total: {data.total}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend />
                <Bar dataKey="fashionbug" name="FashionBug" fill="hsl(var(--primary))" />
                <Bar dataKey="coolplanet" name="CoolPlanet" fill="hsl(var(--accent))" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Color vs Clothing Type */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Color vs Clothing Type</h3>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 80 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis 
                  type="category"
                  dataKey="typeName" 
                  name="Type" 
                  className="text-sm"
                  allowDuplicatedCategory={false}
                />
                <YAxis 
                  type="category"
                  dataKey="colorName" 
                  name="Color" 
                  className="text-sm"
                  allowDuplicatedCategory={false}
                />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Legend />
                <Scatter name="All Products" data={colorByType} fill="hsl(var(--primary))" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          {/* Color vs Clothing Subtype */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Color vs Clothing Subtype</h3>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 80 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis 
                  type="category"
                  dataKey="subtypeName" 
                  name="Subtype" 
                  className="text-sm"
                  angle={-45}
                  textAnchor="end"
                  height={60}
                  allowDuplicatedCategory={false}
                />
                <YAxis 
                  type="category"
                  dataKey="colorName" 
                  name="Color" 
                  className="text-sm"
                  allowDuplicatedCategory={false}
                />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Legend />
                <Scatter name="All Products" data={colorBySubtype} fill="hsl(var(--accent))" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          {/* Color vs Competitor Clothing Type */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Color vs Competitor Clothing Type</h3>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 80 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis 
                  type="category"
                  dataKey="typeName" 
                  name="Type" 
                  className="text-sm"
                  allowDuplicatedCategory={false}
                />
                <YAxis 
                  type="category"
                  dataKey="colorName" 
                  name="Color" 
                  className="text-sm"
                  allowDuplicatedCategory={false}
                />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Legend />
                <Scatter name="FashionBug" data={fashionbugColorType} fill="hsl(var(--primary))" />
                <Scatter name="CoolPlanet" data={coolplanetColorType} fill="hsl(var(--accent))" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          {/* Color vs Competitor Clothing Subtype */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Color vs Competitor Clothing Subtype</h3>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 80 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis 
                  type="category"
                  dataKey="subtypeName" 
                  name="Subtype" 
                  className="text-sm"
                  angle={-45}
                  textAnchor="end"
                  height={60}
                  allowDuplicatedCategory={false}
                />
                <YAxis 
                  type="category"
                  dataKey="colorName" 
                  name="Color" 
                  className="text-sm"
                  allowDuplicatedCategory={false}
                />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Legend />
                <Scatter name="FashionBug" data={fashionbugColorSubtype} fill="hsl(var(--primary))" />
                <Scatter name="CoolPlanet" data={coolplanetColorSubtype} fill="hsl(var(--accent))" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ColorTrends;

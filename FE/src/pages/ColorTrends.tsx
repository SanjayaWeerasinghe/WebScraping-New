import { useState } from "react";
import { FilterBar, Filters } from "@/components/FilterBar";
import { mockData } from "@/data/mockData";
import { filterData } from "@/utils/filterData";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const ColorTrends = () => {
  const [filters, setFilters] = useState<Filters>({
    competitor: "all",
    clothingType: "all",
    clothingSubtype: "all",
  });

  const handleFilterChange = (key: keyof Filters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const filteredData = filterData(mockData, filters);

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

  const CHART_COLORS = ['hsl(var(--primary))', 'hsl(var(--accent))', 'hsl(var(--success))', 'hsl(var(--destructive))', 'hsl(240 15% 60%)', 'hsl(270 50% 50%)'];

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

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 space-y-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Color Trends</h1>
          <p className="text-muted-foreground text-lg">
            Analyze color preferences and trends across product categories
          </p>
        </div>

        <FilterBar filters={filters} onFilterChange={handleFilterChange} />

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
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
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

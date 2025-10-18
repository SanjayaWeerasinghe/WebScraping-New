import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FilterBar, Filters } from "@/components/FilterBar";
import { fetchProducts } from "@/services/api";
import { filterData } from "@/utils/filterData";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const PriceAnalysis = () => {
  const [filters, setFilters] = useState<Filters>({
    competitor: "all",
    clothingType: "all",
    clothingSubtype: "all",
  });

  // Fetch products from API
  const { data: products, isLoading, error } = useQuery({
    queryKey: ['products'],
    queryFn: () => fetchProducts({ limit: 2000 }),
  });

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

  // Create category mappings for X-axis
  const typeMapping = { 'men': 0, 'women': 1 };
  const subtypeMapping = { 'shirt': 0, 'tshirt': 1, 'skirt': 2, 'jean': 3, 'trouser': 4, 'saree': 5, 'frock': 6 };

  // Price vs Clothing Type - each item gets its own dot
  const priceByType = filteredData.map((item) => ({
    typeValue: typeMapping[item.clothingType],
    typeName: item.clothingType,
    price: item.price,
    name: item.name,
  }));

  // Price vs Clothing Subtype - each item gets its own dot
  const priceBySubtype = filteredData.map((item) => ({
    subtypeValue: subtypeMapping[item.clothingSubtype],
    subtypeName: item.clothingSubtype,
    price: item.price,
    name: item.name,
  }));

  // Price vs Competitor Clothing Type
  const fashionbugTypeData = filteredData
    .filter(item => item.competitor === "fashionbug")
    .map((item) => ({ 
      typeValue: typeMapping[item.clothingType],
      typeName: item.clothingType,
      price: item.price,
      name: item.name,
    }));
  
  const coolplanetTypeData = filteredData
    .filter(item => item.competitor === "coolplanet")
    .map((item) => ({ 
      typeValue: typeMapping[item.clothingType],
      typeName: item.clothingType,
      price: item.price,
      name: item.name,
    }));

  // Price vs Competitor Clothing Subtype
  const fashionbugSubtypeData = filteredData
    .filter(item => item.competitor === "fashionbug")
    .map((item) => ({ 
      subtypeValue: subtypeMapping[item.clothingSubtype],
      subtypeName: item.clothingSubtype,
      price: item.price,
      name: item.name,
    }));
  
  const coolplanetSubtypeData = filteredData
    .filter(item => item.competitor === "coolplanet")
    .map((item) => ({ 
      subtypeValue: subtypeMapping[item.clothingSubtype],
      subtypeName: item.clothingSubtype,
      price: item.price,
      name: item.name,
    }));

  // Custom tick formatter
  const typeTickFormatter = (value: number) => {
    return value === 0 ? 'Men' : 'Women';
  };

  const subtypeTickFormatter = (value: number) => {
    const subtypes = ['Shirt', 'T-Shirt', 'Skirt', 'Jean', 'Trouser', 'Saree', 'Frock'];
    return subtypes[value] || '';
  };

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 space-y-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Price Analysis</h1>
          <p className="text-muted-foreground text-lg">
            Compare pricing strategies across competitors and product categories
          </p>
        </div>

        <FilterBar filters={filters} onFilterChange={handleFilterChange} />

        <div className="grid gap-8">
          {/* Price vs Clothing Type */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Price vs Clothing Type</h3>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis 
                  type="category"
                  dataKey="typeName" 
                  name="Type" 
                  className="text-sm"
                  allowDuplicatedCategory={false}
                />
                <YAxis type="number" dataKey="price" name="Price (LKR)" className="text-sm" />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={(value: any, name: string) => {
                    if (name === "Price (LKR)") return [`LKR ${value}`, name];
                    return [value, name];
                  }}
                />
                <Legend />
                <Scatter name="All Products" data={priceByType} fill="hsl(var(--primary))" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          {/* Price vs Clothing Subtype */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Price vs Clothing Subtype</h3>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 20 }}>
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
                <YAxis type="number" dataKey="price" name="Price (LKR)" className="text-sm" />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={(value: any, name: string) => {
                    if (name === "Price (LKR)") return [`LKR ${value}`, name];
                    return [value, name];
                  }}
                />
                <Legend />
                <Scatter name="All Products" data={priceBySubtype} fill="hsl(var(--accent))" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          {/* Price vs Competitor Clothing Type */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Price vs Competitor Clothing Type</h3>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis 
                  type="category"
                  dataKey="typeName" 
                  name="Type" 
                  className="text-sm"
                  allowDuplicatedCategory={false}
                />
                <YAxis type="number" dataKey="price" name="Price (LKR)" className="text-sm" />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={(value: any, name: string) => {
                    if (name === "Price (LKR)") return [`LKR ${value}`, name];
                    return [value, name];
                  }}
                />
                <Legend />
                <Scatter name="FashionBug" data={fashionbugTypeData} fill="hsl(var(--primary))" />
                <Scatter name="CoolPlanet" data={coolplanetTypeData} fill="hsl(var(--accent))" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          {/* Price vs Competitor Clothing Subtype */}
          <div className="bg-card rounded-xl border border-border shadow-md p-6">
            <h3 className="text-xl font-semibold mb-6">Price vs Competitor Clothing Subtype</h3>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 20 }}>
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
                <YAxis type="number" dataKey="price" name="Price (LKR)" className="text-sm" />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={(value: any, name: string) => {
                    if (name === "Price (LKR)") return [`LKR ${value}`, name];
                    return [value, name];
                  }}
                />
                <Legend />
                <Scatter name="FashionBug" data={fashionbugSubtypeData} fill="hsl(var(--primary))" />
                <Scatter name="CoolPlanet" data={coolplanetSubtypeData} fill="hsl(var(--accent))" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PriceAnalysis;

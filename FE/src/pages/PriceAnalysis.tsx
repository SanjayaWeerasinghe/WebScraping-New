import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FilterBar, Filters } from "@/components/FilterBar";
import { fetchProducts, fetchFilterOptions } from "@/services/api";
import { filterData } from "@/utils/filterData";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const PriceAnalysis = () => {
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
    queryKey: ['products-analysis'],
    queryFn: () => fetchProducts({ page: 1, page_size: 10000 }),
  });

  const products = productsData?.items || [];

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

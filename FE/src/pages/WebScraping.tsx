import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProducts, fetchFilterOptions } from "@/services/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const WebScraping = () => {
  const [filters, setFilters] = useState({
    competitor: "all",
    clothingType: "all",
    clothingSubtype: "all",
  });
  const [page, setPage] = useState(1);
  const pageSize = 10;

  // Fetch filter options
  const { data: filterOptions } = useQuery({
    queryKey: ['filter-options'],
    queryFn: fetchFilterOptions,
  });

  // Fetch products with pagination
  const { data: productsData, isLoading, error } = useQuery({
    queryKey: ['products', filters, page],
    queryFn: () => fetchProducts({
      site: filters.competitor !== "all" ? filters.competitor : undefined,
      gender: filters.clothingType !== "all" ? filters.clothingType : undefined,
      clothing_type: filters.clothingSubtype !== "all" ? filters.clothingSubtype : undefined,
      page,
      page_size: pageSize,
    }),
  });

  const products = productsData?.items || [];
  const total = productsData?.total || 0;
  const totalPages = productsData?.total_pages || 1;

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1); // Reset to first page when filter changes
  };

  const competitorColors = {
    fashionbug: "bg-primary/10 text-primary border-primary/20",
    coolplanet: "bg-accent/10 text-accent border-accent/20",
  };

  if (isLoading && !products.length) {
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

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 space-y-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Web Scraping Data</h1>
          <p className="text-muted-foreground text-lg">
            View and filter scraped competitor product data
          </p>
        </div>

        {/* Filters */}
        <div className="bg-card rounded-xl border border-border shadow-md p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Competitor Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Competitor (Site)</label>
              <Select value={filters.competitor} onValueChange={(value) => handleFilterChange("competitor", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="All Competitors" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Competitors</SelectItem>
                  {filterOptions?.competitors.map(comp => (
                    <SelectItem key={comp} value={comp}>{comp === "fashionbug" ? "Fashion Bug" : "Cool Planet"}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Clothing Type Filter (Main Category) */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Clothing Type (Category)</label>
              <Select value={filters.clothingType} onValueChange={(value) => handleFilterChange("clothingType", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {filterOptions?.clothing_types.map(type => (
                    <SelectItem key={type} value={type} className="capitalize">{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Clothing Subtype Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Clothing Subtype</label>
              <Select value={filters.clothingSubtype} onValueChange={(value) => handleFilterChange("clothingSubtype", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="All Subtypes" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Subtypes</SelectItem>
                  {filterOptions?.clothing_subtypes.map(subtype => (
                    <SelectItem key={subtype} value={subtype} className="capitalize">{subtype}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-card rounded-xl border border-border shadow-md overflow-hidden">
          <div className="p-6 border-b border-border flex justify-between items-center">
            <p className="text-sm text-muted-foreground">
              Showing <span className="font-semibold text-foreground">{products.length}</span> of <span className="font-semibold text-foreground">{total}</span> items
            </p>
            <p className="text-sm text-muted-foreground">
              Page {page} of {totalPages}
            </p>
          </div>

          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Competitor</TableHead>
                  <TableHead>Image</TableHead>
                  <TableHead>Product Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Subtype</TableHead>
                  <TableHead>Colours</TableHead>
                  <TableHead className="text-right">Price (LKR)</TableHead>
                  <TableHead>Date Scraped</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {products.map((item) => (
                  <TableRow key={item.id} className="hover:bg-muted/50 transition-colors">
                    <TableCell>
                      <Badge variant="outline" className={competitorColors[item.competitor]}>
                        {item.competitor === "fashionbug" ? "FashionBug" : "CoolPlanet"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {item.imageUrl ? (
                        <img
                          src={item.imageUrl}
                          alt={item.name}
                          className="w-16 h-16 object-cover rounded border border-border"
                          onError={(e) => {
                            e.currentTarget.src = 'https://via.placeholder.com/64?text=No+Image';
                          }}
                        />
                      ) : (
                        <div className="w-16 h-16 bg-muted rounded border border-border flex items-center justify-center text-xs text-muted-foreground">
                          No Image
                        </div>
                      )}
                    </TableCell>
                    <TableCell className="font-medium max-w-xs truncate">{item.name}</TableCell>
                    <TableCell className="capitalize">{item.clothingType}</TableCell>
                    <TableCell className="capitalize">{item.clothingSubtype}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {item.colors.map((color, idx) => (
                          <Badge key={idx} variant="secondary" className="text-xs">
                            {color}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-semibold">
                      Rs {item.price.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">{item.dateScraped}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          <div className="p-6 border-t border-border flex justify-between items-center">
            <Button
              variant="outline"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </Button>

            <div className="flex gap-2">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const pageNum = page <= 3 ? i + 1 : page + i - 2;
                if (pageNum > totalPages) return null;
                return (
                  <Button
                    key={pageNum}
                    variant={pageNum === page ? "default" : "outline"}
                    onClick={() => setPage(pageNum)}
                    className="w-10"
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>

            <Button
              variant="outline"
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebScraping;

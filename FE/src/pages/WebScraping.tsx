import { useState } from "react";
import { FilterBar, Filters } from "@/components/FilterBar";
import { mockData } from "@/data/mockData";
import { filterData } from "@/utils/filterData";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

const WebScraping = () => {
  const [filters, setFilters] = useState<Filters>({
    competitor: "all",
    clothingType: "all",
    clothingSubtype: "all",
  });

  const handleFilterChange = (key: keyof Filters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const filteredData = filterData(mockData, filters);

  const competitorColors = {
    fashionbug: "bg-primary/10 text-primary border-primary/20",
    coolplanet: "bg-accent/10 text-accent border-accent/20",
  };

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 space-y-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Web Scraping Data</h1>
          <p className="text-muted-foreground text-lg">
            View and filter scraped competitor product data
          </p>
        </div>

        <FilterBar filters={filters} onFilterChange={handleFilterChange} />

        <div className="bg-card rounded-xl border border-border shadow-md overflow-hidden">
          <div className="p-6 border-b border-border">
            <p className="text-sm text-muted-foreground">
              Showing <span className="font-semibold text-foreground">{filteredData.length}</span> of {mockData.length} items
            </p>
          </div>

          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Competitor</TableHead>
                  <TableHead>Product Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Subtype</TableHead>
                  <TableHead>Color</TableHead>
                  <TableHead className="text-right">Price (LKR)</TableHead>
                  <TableHead>Date Scraped</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredData.map((item) => (
                  <TableRow key={item.id} className="hover:bg-muted/50 transition-colors">
                    <TableCell>
                      <Badge variant="outline" className={competitorColors[item.competitor]}>
                        {item.competitor === "fashionbug" ? "FashionBug" : "CoolPlanet"}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-medium">{item.name}</TableCell>
                    <TableCell className="capitalize">{item.clothingType}</TableCell>
                    <TableCell className="capitalize">{item.clothingSubtype}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full border border-border" style={{ backgroundColor: item.color.toLowerCase() }} />
                        <span>{item.color}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-semibold">
                      {item.price.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-muted-foreground">{item.dateScraped}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebScraping;

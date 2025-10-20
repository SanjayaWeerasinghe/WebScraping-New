import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";

export interface Filters {
  competitor: string;
  clothingType: string;
  clothingSubtype: string;
  startDate: string;
  endDate: string;
}

export interface FilterOptions {
  competitors: string[];
  clothing_types: string[];
  clothing_subtypes: string[];
}

interface FilterBarProps {
  filters: Filters;
  onFilterChange: (key: keyof Filters, value: string) => void;
  filterOptions?: FilterOptions;
}

export const FilterBar = ({ filters, onFilterChange, filterOptions }: FilterBarProps) => {
  return (
    <div className="flex flex-wrap gap-4 p-6 bg-card rounded-xl border border-border shadow-sm">
      <div className="flex-1 min-w-[200px]">
        <label className="text-sm font-medium text-muted-foreground mb-2 block">
          Competitor
        </label>
        <Select value={filters.competitor} onValueChange={(v) => onFilterChange("competitor", v)}>
          <SelectTrigger>
            <SelectValue placeholder="Select competitor" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Competitors</SelectItem>
            {filterOptions?.competitors.map(comp => (
              <SelectItem key={comp} value={comp}>
                {comp === "fashionbug" ? "Fashion Bug" : "Cool Planet"}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex-1 min-w-[200px]">
        <label className="text-sm font-medium text-muted-foreground mb-2 block">
          Clothing Type
        </label>
        <Select value={filters.clothingType} onValueChange={(v) => onFilterChange("clothingType", v)}>
          <SelectTrigger>
            <SelectValue placeholder="Select type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {filterOptions?.clothing_types.map(type => (
              <SelectItem key={type} value={type} className="capitalize">
                {type}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex-1 min-w-[200px]">
        <label className="text-sm font-medium text-muted-foreground mb-2 block">
          Clothing Subtype
        </label>
        <Select value={filters.clothingSubtype} onValueChange={(v) => onFilterChange("clothingSubtype", v)}>
          <SelectTrigger>
            <SelectValue placeholder="Select subtype" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Subtypes</SelectItem>
            {filterOptions?.clothing_subtypes.map(subtype => (
              <SelectItem key={subtype} value={subtype} className="capitalize">
                {subtype}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex-1 min-w-[200px]">
        <label className="text-sm font-medium text-muted-foreground mb-2 block">
          Start Date
        </label>
        <Input
          type="date"
          value={filters.startDate}
          onChange={(e) => onFilterChange("startDate", e.target.value)}
          className="bg-background"
        />
      </div>

      <div className="flex-1 min-w-[200px]">
        <label className="text-sm font-medium text-muted-foreground mb-2 block">
          End Date
        </label>
        <Input
          type="date"
          value={filters.endDate}
          onChange={(e) => onFilterChange("endDate", e.target.value)}
          className="bg-background"
        />
      </div>
    </div>
  );
};

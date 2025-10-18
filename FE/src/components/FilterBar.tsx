import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export interface Filters {
  competitor: string;
  clothingType: string;
  clothingSubtype: string;
}

interface FilterBarProps {
  filters: Filters;
  onFilterChange: (key: keyof Filters, value: string) => void;
}

export const FilterBar = ({ filters, onFilterChange }: FilterBarProps) => {
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
            <SelectItem value="fashionbug">FashionBug</SelectItem>
            <SelectItem value="coolplanet">CoolPlanet</SelectItem>
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
            <SelectItem value="men">Men</SelectItem>
            <SelectItem value="women">Women</SelectItem>
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
            <SelectItem value="shirt">Shirt</SelectItem>
            <SelectItem value="tshirt">T-Shirt</SelectItem>
            <SelectItem value="skirt">Skirt</SelectItem>
            <SelectItem value="jean">Jean</SelectItem>
            <SelectItem value="trouser">Trouser</SelectItem>
            <SelectItem value="saree">Saree</SelectItem>
            <SelectItem value="frock">Frock</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};

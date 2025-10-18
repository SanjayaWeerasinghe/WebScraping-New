import { ScrapedItem } from "@/data/mockData";
import { Filters } from "@/components/FilterBar";

export const filterData = (data: ScrapedItem[], filters: Filters): ScrapedItem[] => {
  return data.filter(item => {
    if (filters.competitor !== "all" && item.competitor !== filters.competitor) return false;
    if (filters.clothingType !== "all" && item.clothingType !== filters.clothingType) return false;
    if (filters.clothingSubtype !== "all" && item.clothingSubtype !== filters.clothingSubtype) return false;
    return true;
  });
};

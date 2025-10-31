'use client'

import { OpportunityFilters as Filters } from '@/types'
import { Card } from '@/components/ui/card'
import { Filter, SlidersHorizontal } from 'lucide-react'

interface OpportunityFiltersProps {
  filters: Filters
  onFiltersChange: (filters: Filters) => void
}

export function OpportunityFilters({ filters, onFiltersChange }: OpportunityFiltersProps) {
  const updateFilter = (key: keyof Filters, value: any) => {
    onFiltersChange({ ...filters, [key]: value })
  }

  return (
    <Card className="p-6 mb-6">
      <div className="flex items-center gap-2 mb-4">
        <SlidersHorizontal className="w-5 h-5" />
        <h2 className="text-lg font-semibold">Filters</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        {/* Position Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Position
          </label>
          <select
            value={filters.position || ''}
            onChange={(e) => updateFilter('position', e.target.value || undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Positions</option>
            <option value="QB">QB</option>
            <option value="RB">RB</option>
            <option value="WR">WR</option>
            <option value="TE">TE</option>
          </select>
        </div>

        {/* Stat Type Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Stat Type
          </label>
          <select
            value={filters.stat_type || ''}
            onChange={(e) => updateFilter('stat_type', e.target.value || undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Stats</option>
            <option value="passing_yards">Passing Yards</option>
            <option value="passing_touchdowns">Passing TDs</option>
            <option value="rushing_yards">Rushing Yards</option>
            <option value="rushing_touchdowns">Rushing TDs</option>
            <option value="receiving_yards">Receiving Yards</option>
            <option value="receptions">Receptions</option>
            <option value="receiving_touchdowns">Receiving TDs</option>
          </select>
        </div>

        {/* Slate Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Game Slate
          </label>
          <select
            value={filters.slate || ''}
            onChange={(e) => updateFilter('slate', e.target.value || undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Slates</option>
            <option value="THURSDAY">Thursday Night</option>
            <option value="SATURDAY">Saturday</option>
            <option value="SUNDAY_EARLY">Sunday Early (1PM ET)</option>
            <option value="SUNDAY_LATE">Sunday Late (4PM ET)</option>
            <option value="SUNDAY_NIGHT">Sunday Night</option>
            <option value="MONDAY">Monday Night</option>
          </select>
        </div>

        {/* Minimum Confidence */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Min Confidence: {filters.min_confidence || 0}%
          </label>
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={filters.min_confidence || 0}
            onChange={(e) => updateFilter('min_confidence', parseInt(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>

        {/* Minimum Edge */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Min Edge: {filters.min_edge?.toFixed(1) || 0.0}
          </label>
          <input
            type="range"
            min="0"
            max="20"
            step="0.5"
            value={filters.min_edge || 0}
            onChange={(e) => updateFilter('min_edge', parseFloat(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0</span>
            <span>10</span>
            <span>20+</span>
          </div>
        </div>

        {/* Sort By */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sort By
          </label>
          <select
            value={filters.sort_by || 'edge'}
            onChange={(e) => updateFilter('sort_by', e.target.value as 'edge' | 'confidence' | 'game_time')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="edge">Edge (Highest)</option>
            <option value="confidence">Confidence (Highest)</option>
            <option value="game_time">Game Time (Soonest)</option>
          </select>
        </div>
      </div>

      {/* Active Filter Count */}
      <div className="mt-4 flex items-center justify-between">
        <div className="text-sm text-gray-600">
          {Object.values(filters).filter(v => v !== undefined && v !== '' && v !== 0).length > 0 ? (
            <span>
              {Object.values(filters).filter(v => v !== undefined && v !== '' && v !== 0).length} filter(s) active
            </span>
          ) : (
            <span>No filters active</span>
          )}
        </div>

        {Object.values(filters).some(v => v !== undefined && v !== '' && v !== 0) && (
          <button
            onClick={() => onFiltersChange({})}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Clear All
          </button>
        )}
      </div>
    </Card>
  )
}

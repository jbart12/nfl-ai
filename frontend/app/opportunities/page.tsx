'use client'

import { useState, useEffect } from 'react'
import { fetchOpportunities } from '@/lib/api'
import { Opportunity, OpportunityFilters } from '@/types'
import { OpportunityCard } from '@/components/opportunities/OpportunityCard'
import { OpportunityFilters as FiltersComponent } from '@/components/opportunities/OpportunityFilters'
import { Loader2, TrendingUp, AlertCircle } from 'lucide-react'

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<OpportunityFilters>({
    sort_by: 'edge',
    limit: 50,
  })

  useEffect(() => {
    loadOpportunities()
  }, [filters])

  const loadOpportunities = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchOpportunities(filters)
      setOpportunities(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load opportunities')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-8 h-8 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">Opportunities Feed</h1>
          </div>
          <p className="text-gray-600 text-lg">
            AI-powered predictions showing the best betting edges
          </p>
        </div>

        {/* Filters */}
        <FiltersComponent filters={filters} onFiltersChange={setFilters} />

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-3 text-gray-600">Loading opportunities...</span>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-6 h-6 text-red-600" />
              <div>
                <h3 className="font-semibold text-red-900">Error Loading Opportunities</h3>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
            <button
              onClick={loadOpportunities}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && opportunities.length === 0 && (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No Opportunities Found</h3>
            <p className="text-gray-500 mb-6">
              Try adjusting your filters or check back later for new predictions.
            </p>
            <button
              onClick={() => setFilters({ sort_by: 'edge', limit: 50 })}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Clear Filters
            </button>
          </div>
        )}

        {/* Opportunities Grid */}
        {!loading && !error && opportunities.length > 0 && (
          <>
            <div className="mb-4 text-sm text-gray-600">
              Showing {opportunities.length} opportunit{opportunities.length === 1 ? 'y' : 'ies'}
            </div>
            <div className="grid grid-cols-1 gap-6">
              {opportunities.map((opportunity) => (
                <OpportunityCard key={opportunity.id} opportunity={opportunity} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

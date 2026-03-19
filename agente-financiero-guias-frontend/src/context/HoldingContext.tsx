'use client'

/**
 * HoldingContext — Multi-company financial context
 * Manages which company/business is currently selected
 */

import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import type { Company } from '@/types'

interface HoldingContextType {
    selectedCompany: Company | null
    setSelectedCompany: (company: Company) => void
    companies: Company[]
    setCompanies: (companies: Company[]) => void
}

const HoldingContext = createContext<HoldingContextType | undefined>(undefined)

export function HoldingProvider({ children }: { children: ReactNode }) {
    const [selectedCompany, setSelectedCompanyState] = useState<Company | null>(null)
    const [companies, setCompaniesState] = useState<Company[]>([])

    const setSelectedCompany = useCallback((company: Company) => {
        setSelectedCompanyState(company)
        // Persist in sessionStorage for tab-level persistence
        if (typeof window !== 'undefined') {
            sessionStorage.setItem('holding_selected_company', company.id)
        }
    }, [])

    const setCompanies = useCallback((companiesList: Company[]) => {
        setCompaniesState(companiesList)
        // Auto-select if none selected
        if (!selectedCompany && companiesList.length > 0) {
            const savedId = typeof window !== 'undefined'
                ? sessionStorage.getItem('holding_selected_company')
                : null
            const match = savedId ? companiesList.find(c => c.id === savedId) : null
            setSelectedCompanyState(match || companiesList[0])
        }
    }, [selectedCompany])

    return (
        <HoldingContext.Provider value={{
            selectedCompany, setSelectedCompany, companies, setCompanies
        }}>
            {children}
        </HoldingContext.Provider>
    )
}

export function useHoldingContext() {
    const context = useContext(HoldingContext)
    if (context === undefined) {
        throw new Error('useHoldingContext must be used within a HoldingProvider')
    }
    return context
}

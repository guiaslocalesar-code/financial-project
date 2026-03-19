'use client'

import { Fragment, useMemo } from 'react'
import { Listbox, Transition } from '@headlessui/react'
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/react/20/solid'
import { BuildingOffice2Icon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { useHoldingContext } from '@/context/HoldingContext'

export default function CompanySelector() {
    const { selectedCompany, setSelectedCompany, companies } = useHoldingContext()

    if (companies.length === 0) {
        return (
            <div className="text-sm text-gray-500 bg-gray-50 rounded-lg p-3 border border-gray-100 italic text-center">
                Sin empresas
            </div>
        )
    }

    return (
        <Listbox value={selectedCompany} onChange={setSelectedCompany}>
            <div className="relative">
                <Listbox.Button className="relative w-full cursor-default rounded-xl bg-white/80 backdrop-blur-md pl-3 pr-10 text-left border border-gray-200/50 shadow-sm hover:border-blue-400/50 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-sm h-[52px] flex items-center">
                    <div className="flex items-center gap-3 w-full">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0 shadow-sm">
                            {selectedCompany?.name?.substring(0, 2).toUpperCase() || '??'}
                        </div>
                        <div className="flex flex-col min-w-0">
                            <span className="block truncate font-semibold text-gray-800 leading-tight text-sm">
                                {selectedCompany ? selectedCompany.name : 'Seleccionar Empresa'}
                            </span>
                            <span className="text-[10px] text-gray-400 truncate">
                                {selectedCompany?.cuit || ''}
                            </span>
                        </div>
                    </div>
                    <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                        <ChevronUpDownIcon className="h-5 w-5 text-gray-400" />
                    </span>
                </Listbox.Button>

                <Transition as={Fragment}
                    enter="transition ease-out duration-150" enterFrom="opacity-0 translate-y-1" enterTo="opacity-100 translate-y-0"
                    leave="transition ease-in duration-100" leaveFrom="opacity-100 translate-y-0" leaveTo="opacity-0 translate-y-1"
                >
                    <Listbox.Options className="absolute mt-2 max-h-72 w-full overflow-auto rounded-xl bg-white py-2 text-sm shadow-xl ring-1 ring-black/5 focus:outline-none z-50">
                        {companies.map((company) => (
                            <Listbox.Option
                                key={company.id}
                                value={company}
                                className={({ active }) =>
                                    clsx(
                                        'relative cursor-default select-none py-3 pl-4 pr-10 mx-2 rounded-lg transition-colors',
                                        active ? 'bg-blue-50 text-blue-900' : 'text-gray-900'
                                    )
                                }
                            >
                                {({ selected }) => (
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
                                            {company.name.substring(0, 2).toUpperCase()}
                                        </div>
                                        <div className="flex flex-col min-w-0">
                                            <span className={clsx('block truncate', selected ? 'font-bold' : 'font-medium')}>
                                                {company.name}
                                            </span>
                                            <span className="text-xs text-gray-400">CUIT: {company.cuit}</span>
                                        </div>
                                        {selected && (
                                            <span className="absolute inset-y-0 right-3 flex items-center text-blue-600">
                                                <CheckIcon className="h-5 w-5" />
                                            </span>
                                        )}
                                    </div>
                                )}
                            </Listbox.Option>
                        ))}
                    </Listbox.Options>
                </Transition>
            </div>
        </Listbox>
    )
}

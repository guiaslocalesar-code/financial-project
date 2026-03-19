'use client'

import { useState, useCallback, useRef } from 'react'
import { PhotoIcon, XMarkIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import { api } from '@/services/api'

interface ImageUploadProps {
    value?: string
    onChange: (url: string) => void
    label: string
}

export function ImageUpload({ value, onChange, label }: ImageUploadProps) {
    const [isDragging, setIsDragging] = useState(false)
    const [isUploading, setIsUploading] = useState(false)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const handleUpload = async (file: File) => {
        if (!file.type.startsWith('image/')) {
            alert('Por favor selecciona una imagen válida.')
            return
        }

        setIsUploading(true)
        try {
            const formData = new FormData()
            formData.append('file', file)
            
            // Assuming your api service has an upload method or using axios directly
            // For now, let's use a direct fetch or custom api call
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/upload`, {
                method: 'POST',
                body: formData,
            })
            
            if (!response.ok) throw new Error('Error al subir imagen')
            
            const data = await response.json()
            onChange(data.url)
        } catch (error) {
            console.error('Upload error:', error)
            alert('Error al subir la imagen. Inténtalo de nuevo.')
        } finally {
            setIsUploading(false)
        }
    }

    const onDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(true)
    }, [])

    const onDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
    }, [])

    const onDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
        const file = e.dataTransfer.files?.[0]
        if (file) handleUpload(file)
    }, [])

    const onFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) handleUpload(file)
    }

    const removeImage = () => {
        onChange('')
        if (fileInputRef.current) fileInputRef.current.value = ''
    }

    return (
        <div className="space-y-2">
            <label className="block text-sm font-medium leading-6 text-gray-900">
                {label}
            </label>
            
            <div
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onDrop={onDrop}
                className={clsx(
                    "relative flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed transition-all duration-200 min-h-[160px]",
                    isDragging ? "border-blue-500 bg-blue-50/50" : "border-gray-300 hover:border-gray-400 bg-gray-50/30",
                    value ? "py-4" : "py-8"
                )}
                onClick={() => !value && fileInputRef.current?.click()}
            >
                {isUploading ? (
                    <div className="flex flex-col items-center gap-3">
                        <div className="w-8 h-8 border-2 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
                        <p className="text-sm font-medium text-gray-500">Subiendo...</p>
                    </div>
                ) : value ? (
                    <div className="relative group w-full px-4 flex flex-col items-center">
                        <img 
                            src={value.startsWith('http') ? value : `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${value}`} 
                            alt="Preview" 
                            className="max-h-32 rounded-xl object-contain shadow-sm bg-white p-2"
                        />
                        <button
                            type="button"
                            onClick={(e) => {
                                e.stopPropagation()
                                removeImage()
                            }}
                            className="absolute -top-2 -right-2 p-1.5 bg-rose-500 text-white rounded-full shadow-lg hover:bg-rose-600 transition-colors opacity-0 group-hover:opacity-100 sm:opacity-100"
                        >
                            <XMarkIcon className="w-4 h-4" />
                        </button>
                        <button
                            type="button"
                            onClick={(e) => {
                                e.stopPropagation()
                                fileInputRef.current?.click()
                            }}
                            className="mt-3 text-xs font-semibold text-blue-600 hover:text-blue-700 underline underline-offset-4"
                        >
                            Cambiar imagen
                        </button>
                    </div>
                ) : (
                    <div className="flex flex-col items-center text-center px-6">
                        <div className="w-12 h-12 rounded-2xl bg-white shadow-sm border border-gray-100 flex items-center justify-center mb-3 text-gray-400">
                            <ArrowUpTrayIcon className="w-6 h-6" />
                        </div>
                        <p className="text-sm font-semibold text-gray-900">
                            Haz clic para subir o arrastra y suelta
                        </p>
                        <p className="mt-1 text-xs text-gray-500 font-medium">
                            PNG, JPG o SVG hasta 2MB
                        </p>
                    </div>
                )}
                
                <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept="image/*"
                    onChange={onFileSelect}
                />
            </div>
        </div>
    )
}

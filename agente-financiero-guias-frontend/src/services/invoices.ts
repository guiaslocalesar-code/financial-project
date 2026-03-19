import { api } from './api';
import { ClientService, Invoice } from '@/types';

/**
 * Helper to generate a draft invoice from multiple contracts belonging to the same client
 */
export async function createInvoiceFromContracts(
    clientContracts: ClientService[], 
    companyId: string,
    month: number,
    year: number
) {
    if (clientContracts.length === 0) return null;
    
    const client = clientContracts[0].client;
    const clientId = clientContracts[0].client_id;
    const currency = clientContracts[0].currency || 'ARS';

    // 1. Prepare Issue Date (1st of the month)
    const issueDate = new Date(year, month - 1, 1).toISOString().split('T')[0];
    
    // 2. Prepare Due Date (+10 days)
    const dueDate = new Date(year, month - 1, 11).toISOString().split('T')[0];

    // 3. Build invoice items
    const items = clientContracts.map(contract => ({
        service_id: contract.service_id,
        description: contract.service?.name || contract.service_name || 'Servicio Mensual',
        quantity: 1,
        unit_price: contract.monthly_fee,
        iva_rate: 21.0
    }));

    // 4. Build invoice payload
    const payload = {
        company_id: companyId,
        client_id: clientId,
        invoice_type: 'C', 
        point_of_sale: 1, 
        issue_date: issueDate,
        due_date: dueDate,
        currency: currency,
        notes: `Facturación mensual recurrente - ${month}/${year}`,
        items: items
    };

    console.log(`[Batch] Creando borrador agrupado para ${client?.name || clientId} (${items.length} ítems)`);
    const response = await api.invoices.create(payload);
    return response.data;
}

/**
 * Batch generation logic with grouping by client
 */
export async function generateInvoiceBatch(
    contracts: ClientService[], 
    companyId: string,
    existingInvoices: Invoice[],
    month: number,
    year: number
) {
    const results = {
        created: 0,
        skipped: 0,
        ids: [] as string[]
    };

    // 1. Group contracts by client_id
    const contractsByClient: Record<string, ClientService[]> = {};
    contracts.forEach(c => {
        if (!contractsByClient[c.client_id]) {
            contractsByClient[c.client_id] = [];
        }
        contractsByClient[c.client_id].push(c);
    });

    const clientIds = Object.keys(contractsByClient);
    console.log(`[Batch] Iniciando generación masiva para ${month}/${year}. Clientes únicos: ${clientIds.length}`);

    for (const clientId of clientIds) {
        const clientContracts = contractsByClient[clientId];
        const clientName = clientContracts[0].client?.name || clientId;

        // 2. Double check duplicate: does THIS client already have a draft for THIS month?
        // We look for ANY invoice from this client in this month/year.
        // A more strict check would be checking if it contains the same services.
        const alreadyExists = existingInvoices.some(inv => {
            const invDate = new Date(inv.issue_date);
            const isSameMonth = (invDate.getMonth() + 1) === month;
            const isSameYear = invDate.getFullYear() === year;
            return inv.client_id === clientId && isSameMonth && isSameYear;
        });

        if (alreadyExists) {
            console.log(`[Batch] Saltando cliente ${clientName} (Ya existe borrador este mes)`);
            results.skipped += clientContracts.length;
            continue;
        }

        try {
            const invoice = await createInvoiceFromContracts(clientContracts, companyId, month, year);
            if (invoice) {
                results.created++;
                results.ids.push(invoice.id || invoice.data?.id);
            }
        } catch (error) {
            console.error(`[Batch] Error creando factura para cliente ${clientName}:`, error);
        }
    }

    console.log(`[Batch] Proceso terminado. Facturas creadas: ${results.created}, Contratos saltados/procesados sumados: ${results.created + results.skipped}`);
    return results;
}

export const formatCurrency = (val: number) => 
    val.toLocaleString('es-AR', { style: 'currency', currency: 'ARS' });

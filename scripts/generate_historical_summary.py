import asyncio
from sqlalchemy import select, func, extract
from app.database import SessionLocal
from app.models.commission import Commission

async def generate_summary():
    async with SessionLocal() as db:
        # Get total commissions generated
        count_res = await db.execute(select(func.count(Commission.id)))
        total_count = count_res.scalar()
        
        # Group by year-month
        # PostgreSQL syntax for year and month
        query = (
            select(
                extract('year', Commission.created_at).label('year'),
                extract('month', Commission.created_at).label('month'),
                func.count(Commission.id).label('count'),
                func.sum(Commission.commission_amount).label('total_amount')
            )
            .group_by('year', 'month')
            .order_by('year', 'month')
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        report = f"# Resumen de Carga Histórica de Comisiones\n\n"
        report += f"**Total de comisiones generadas en la base de datos:** {total_count}\n\n"
        report += "### Desglose Mensual (según fecha de creación/ingreso original)\n"
        report += "| Año | Mes | Cantidad Operaciones | Monto Total de Comisiones ($) |\n"
        report += "|---|---|---|---|\n"
        
        total_amount = 0
        for r in rows:
            y = int(r.year) if r.year else 0
            m = int(r.month) if r.month else 0
            amount = float(r.total_amount)
            total_amount += amount
            report += f"| {y} | {m:02d} | {r.count} | ${amount:,.2f} |\n"
            
        report += f"\n**Gran Total:** ${total_amount:,.2f}\n"

        report_file = "resumen_historico_comisiones.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
            
        print(f"Resumen generado en: {report_file}")

if __name__ == "__main__":
    asyncio.run(generate_summary())

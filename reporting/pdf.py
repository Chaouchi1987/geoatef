from __future__ import annotations
from io import BytesIO
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
FONT=Path(__file__).resolve().parents[2]/"assets"/"DejaVuSans.ttf"
def make_pdf(report):
    buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=14*mm,leftMargin=14*mm,topMargin=14*mm,bottomMargin=14*mm); styles=getSampleStyleSheet(); font="Helvetica"
    if FONT.exists():
        from reportlab.pdfbase import pdfmetrics; from reportlab.pdfbase.ttfonts import TTFont
        try: pdfmetrics.registerFont(TTFont("GeoDejaVu",str(FONT))); font="GeoDejaVu"; [setattr(styles[k],"fontName",font) for k in ["Title","Heading2","Heading3","BodyText"]]
        except Exception: pass
    story=[Paragraph("GeoAnomaly Pro — Scientific Geospatial Anomaly Analysis",styles["Title"]),Paragraph("Created by Chaouchi Atef",styles["BodyText"]),Spacer(1,8),Paragraph(report.get("scientific_boundary",""),styles["BodyText"]),Spacer(1,10)]
    md=report.get("metadata",{}); cu=md.get("centre_utm",{})
    rows=[["Parameter","Value"],["Analysis duration",f"{md.get('duration_seconds','—')} s"],["AOI center",f"{md.get('aoi_center',{}).get('latitude','—')}, {md.get('aoi_center',{}).get('longitude','—')}"],["AOI radius",f"{md.get('aoi_radius_m','—')} m"],["UTM",cu.get("label","—")],["Sampling scale",f"{md.get('analysis_scale_m','—')} m"],["Date range",f"{md.get('start_date','—')} → {md.get('end_date','—')}"],["Real samples",str(md.get('sample_count','—'))],["Earth Engine observations",str(md.get('observation_count','—'))],["Synthetic data",str(md.get('synthetic',False))]]
    tb=Table(rows,colWidths=[58*mm,112*mm]); tb.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#006233")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#9aaebe")),("FONTSIZE",(0,0),(-1,-1),8),("FONTNAME",(0,0),(-1,-1),font)])); story += [tb,Spacer(1,10),Paragraph("Processing methodology",styles["Heading2"])]
    for x in report.get("methodology",[]): story.append(Paragraph("• "+x,styles["BodyText"]))
    story += [Spacer(1,10),Paragraph("Top evidence-supported targets",styles["Heading2"])]
    for x in report.get("targets",[]):
        it=x.get("type_interpretation",{}); rows=[["Strength",f"{x.get('strength_percent','—')}%"],["Surface footprint",f"{x.get('estimated_surface_length_m','—')} × {x.get('estimated_surface_width_m','—')} m"],["UTM",x.get('utm',{}).get('label','—')],["Interpretation",it.get('label','—')],["Interpretation fit",f"{it.get('fit_percent','—')}%"],["Depth","Not estimated from satellite-only data"],["Evidence","; ".join(x.get('evidence',[]))],["Trace ID",x.get('trace_id','—')]]; story += [Paragraph(x.get('target_id','Target'),styles["Heading3"]),Table(rows,colWidths=[48*mm,122*mm]),Spacer(1,7),Paragraph(it.get('scientific_note',''),styles["BodyText"]),Spacer(1,9)]
    story.append(Paragraph("Scientific limitations",styles["Heading2"])); [story.append(Paragraph("• "+x,styles["BodyText"])) for x in report.get("limitations",[])]; doc.build(story); return buf.getvalue()

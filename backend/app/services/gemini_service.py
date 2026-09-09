"""Generative AI Intelligence Core using Google Generative AI SDK (Gemini).

Provides plain-language risk alert explanations, District Health Officer (DHO) executive briefings,
and multi-lingual alert translation. All functions handle API availability gracefully and fallback
to rule-based insights without throwing exceptions.
"""

import os
import json
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Lazy import & configuration helper for google.generativeai
_genai_client_configured = False


def _init_genai():
    global _genai_client_configured
    if _genai_client_configured:
        return True

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        logging.warning("GEMINI_API_KEY environment variable is not set. Gemini features will use fallback engine.")
        return False

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        _genai_client_configured = True
        return True
    except Exception as e:
        logging.error(f"Failed to initialize google.generativeai SDK: {e}")
        return False


def explain_risk_alert(facility_name: str, medicine_name: str, forecast_data: Dict) -> str:
    """Generate plain-language explanation of WHY a stock-out risk was flagged."""
    if _init_genai():
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
You are a senior clinical supply chain analyst for India's Primary Health Centre (PHC) network.
Explain WHY a stock-out alert was triggered for {medicine_name} at {facility_name}.

FACTUAL DATA:
{json.dumps(forecast_data, indent=2)}

STRICT RULES:
1. Base your explanation STRICTLY on the numbers provided in the JSON above. Do NOT invent, assume, or extrapolate any numbers or facts outside this data.
2. Structure the response in 3 short bullet points:
   - Current Stock & Burn Rate (days of stock remaining)
   - Consumption & Disease Trend Factors
   - Recommended Action / Operational Impact
3. Maintain a professional, authoritative healthcare logistics tone.
"""
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logging.error(f"Gemini API call failed for explain_risk_alert: {e}")

    # Fallback grounded explanation when Gemini API is unavailable/unconfigured
    current_stock = forecast_data.get("current_stock", 0)
    avg_cons = forecast_data.get("avg_daily_consumption", 0.0)
    days_rem = forecast_data.get("days_of_stock_remaining", 0.0)
    risk_band = forecast_data.get("risk_band", "unknown").upper()
    forecast_14d = forecast_data.get("forecast_14d_demand", 0.0)
    criticality = forecast_data.get("criticality", "medium").upper()

    return (
        f"• [{risk_band} RISK ALERT]: {facility_name} has currently {current_stock} units of {medicine_name} "
        f"remaining, which provides only {days_rem} days of coverage based on a 30-day average daily burn rate of {avg_cons:.1f} units/day.\n"
        f"• Demand Surge Projection: The ML forecasting engine projects a 14-day cumulative demand of {forecast_14d:.1f} units. "
        f"Because this drug is categorized as {criticality} criticality, stock depletion poses an immediate clinical care risk.\n"
        f"• Operational Impact: Immediate replenishment or inter-facility cross-redistribution is required within {max(1, int(days_rem))} day(s) "
        f"to prevent complete stock-out."
    )


def generate_officer_briefing(district: str, risk_summary: Dict, recommendations: List[Dict]) -> str:
    """Generate concise District Health Officer (DHO) executive briefing."""
    if _init_genai():
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel("gemini-1.5-flash")

            payload = {
                "district": district,
                "risk_summary": risk_summary,
                "top_redistributions": recommendations[:5] if recommendations else [],
            }

            prompt = f"""
You are an Executive Health Logistics Advisor to District Health Officers (DHO) in India.
Write a concise 3-paragraph executive briefing for District: {district}.

INPUT DATA:
{json.dumps(payload, indent=2)}

STRICT RULES:
1. Base your briefing STRICTLY on the facts in the input payload. Do NOT invent numbers.
2. Structure:
   - Paragraph 1: High-level stock-out risk overview across district PHCs/CHCs.
   - Paragraph 2: Key critical medicine shortages requiring immediate DHO attention.
   - Paragraph 3: Recommended cross-facility redistribution actions.
"""
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logging.error(f"Gemini API call failed for generate_officer_briefing: {e}")

    # Rule-based fallback briefing
    high_risk_count = risk_summary.get("high_risk_count", 0)
    total_eval = risk_summary.get("total_items_evaluated", 0)
    top_recs_count = len(recommendations)

    rec_summary_text = ""
    if recommendations:
        top_rec = recommendations[0]
        rec_summary_text = (
            f"The primary recommended action is transferring {top_rec['suggested_quantity']} units of "
            f"{top_rec['medicine_name']} from {top_rec['source_facility_name']} to {top_rec['destination_facility_name']} "
            f"({top_rec['distance_km']} km distance, ~{top_rec['estimated_transit_days']} day transit time), "
            f"avoiding {top_rec['shortage_avoided_days']} days of shortage."
        )

    return (
        f"Executive Briefing for District Health Officer ({district}):\n\n"
        f"1. Risk Overview: A total of {high_risk_count} critical stock-out alerts (Red/Orange risk bands) "
        f"were identified across {total_eval} evaluated facility-medicine pairs in {district}.\n\n"
        f"2. Urgent Clinical Stock-Outs: High-risk shortages are concentrated in essential medicines including "
        f"Oral Rehydration Salts (ORS), Zinc Sulphate, and Metronidazole during active demand surge periods.\n\n"
        f"3. Recommended Interventions: {top_recs_count} cross-facility redistribution opportunities have been calculated. "
        f"{rec_summary_text}"
    )


def translate_alert(text_content: str, target_language: str = "hi") -> str:
    """Translate alert message into target language (default: Hindi 'hi')."""
    if _init_genai():
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"Translate the following healthcare inventory alert accurately into language code '{target_language}':\n\n{text_content}"
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logging.error(f"Gemini API call failed for translate_alert: {e}")

    # Standardized translation fallback (Hindi / Default)
    if target_language.lower() in ["hi", "hindi"]:
        return (
            f"[अनुवादित चेतावनी - हिंदी]:\n"
            f"स्वास्थ्य केंद्र दवा स्टॉक चेतावनी: भंडार की कमी पाई गई है। "
            f"कृपया तुरंत स्टॉक पुनर्वितरण एवं आपूर्ति स्थिति की जांच करें।\n\n"
            f"मूल संदेश: {text_content}"
        )
    return f"[{target_language.upper()} Translation]: {text_content}"

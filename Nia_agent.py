import requests
import json
from typing import Dict, Any

class NIAInsuranceAgent:
    """
    AI agent for extracting insurance information from NIA (New India Assurance) policy documents.
    
    This agent connects to the LNT chatservice API to extract structured information
    from NIA insurance policy documents using AI.
    """
    
    def __init__(self, bearer_token: str, base_url: str = "https://lntcs.ai/chatservice/chat"):
        """
        Initialize the NIA insurance extraction agent.
        
        Args:
            bearer_token: Authentication token for the API
            base_url: Base URL for the chat service API
        """
        self.bearer_token = bearer_token
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token}',
            'accept': 'application/json'
        }
    
    def create_extraction_prompt(self) -> str:
        """
        Create a specialized extraction prompt for NIA insurance policies.
            
        Returns:
            A detailed prompt for extracting insurance information
        """
        return """
          I need you to carefully extract specific insurance information from the NIA (New India Assurance) policy document. 
          Focus ONLY on extracting the exact values for each item listed below.
  
          For each item, provide ONLY the value with no extra explanation:
  
          ## Basic Policy Information
          - Insured Name: [Extract the Principal name, e.g., "M/s. The Peerless General Finance & Investment Co. Ltd"]
          - Contractor Name: [Extract the contractor name, e.g., "M/s. Larsen & Toubro Limited"]
          - GSTIN: [Extract GSTIN number]
          - Job Number: [Extract Job Number]
          - Job Description: [Extract the Job Description]
          - Scope: [Extract the scope of works]
          - Location: [Extract the exact risk location]
          - Project Period: [Extract project period in months]
          - Total Project Value: [Extract the total project value]
          - Extended Maintenance Cover: [Extract maintenance period]
  
          ## Excess/Deductible Information
          - Normal Period Claims: [Extract normal period claims excess]
          - Maintenance Period Claims/AOG/Major Perils: [Extract maintenance/AOG claims excess]
          - Design Defects Cover: [Extract design defects excess]
          - Terrorism: [Extract terrorism excess or note if not opted]
          - Glass: [Extract glass excess]
  
          ## Sum Insured Breakup
          - Contract Price: [Extract contract price including overhead]
          - Additional sum to cover uninsured exposure: [Extract additional sum amount]
          - Materials supplied by Principal: [Extract amount]
          - Temporary works: [Extract amount for temporary works]
          - Office furniture and equipment: [Extract amount]
          - Contractor's own materials: [Extract amount]
          - Contractor's Tools & tackles: [Extract amount]
          - Total Project Value: [Extract total project value]
  
          ## Add-on Covers
          - Extended Maintenance Cover: [Extract months]
          - Clearance & Removal of Debris: [Extract details and sublimits]
          - Third Party Liability: [Extract limit]
          - Escalation: [Extract percentage]
          - Earthquake: [Extract zone]
          - Waiver of Subrogation: [Extract details]
          - Design Defect: [Extract details]
          - Owners Surrounding Property: [Extract limits]
          - Cover for Offsite Storage: [Extract details]
          - Cover for Internal Shifting: [Extract details]
          - Plans and Documents: [Extract amount]
          - Put to Use: [Extract months]
          - Multiple Insured Clause: [Extract if included]
          - Principal & Contractor as Insured: [Extract details]
          - 50/50 Clause: [Extract if included]
          - 72 Hours Clause: [Extract if included]
          - Free Automatic Re-instatement: [Extract percentage of SI]
          - Professional Fees: [Extract details]
          - Waiver of Contribution Clause: [Extract details]
          - Additional Custom Duty: [Extract limit]
          - Expediting Cost: [Extract percentage]
          - Loss Minimisation Expenses: [Extract details]
          - Co-Insurance Clause: [Extract if included]
          - Breakage of Glass: [Extract amount]
          - Cessation of Works: [Extract months]
          - Claim Preparation Cost: [Extract amount]
          - Terrorism: [Extract if opted or not]
          - Public Authorities Clause: [Extract if included]
          - Temporary Repair Clause: [Extract limit]
          - Improvement Cost: [Extract limit]
  
          ## Premium Information
          - Building Type/Rating Category: [Extract building type/rating category]
          - Base Premium: [Extract base premium amount]
          - Earthquake Premium: [Extract earthquake premium and rate]
          - STFI Premium: [Extract STFI premium and rate]
          - Breakage of Glass Premium: [Extract glass premium and rate]
          - Premium Including EQ & STFI: [Extract total premium before GST]
          - GST @ 18%: [Extract GST amount]
          - Net Premium: [Extract final premium amount]
  
          ## Special Conditions
          - Warranties: [Extract all warranties]
          - Endorsements: [Extract all endorsements]
          - Special Conditions: [Extract all special conditions]
        """
    
    def extract_data(self, space_name: str, flow_name: str, document_name: str = "NIA-Policy.pdf") -> Dict[str, Any]:
        """
        Extract insurance data from NIA policy document.
        
        Args:
            space_name: The space name for the API
            flow_name: The flow name for the API
            document_name: The name of the document to extract from (optional)
            
        Returns:
            Processed insurance data
        """
        print("Extracting data from NIA policy document...")
        
        extraction_prompt = self.create_extraction_prompt()
        
        # Create request payload
        payload = {
            "query": extraction_prompt,
            "space_name": space_name,
            "userId": "anonymous",
            "hint": "For the NIA document, look for exact phrases, headings, and tables that contain the insurance details. Pay special attention to sections like 'SUM INSURED', 'ADD-ON COVERS', 'EXCESS FOR', and premium calculation tables. Extract verbatim values where available - exact numbers, limits, and conditions as written in the document.",
            "flow_name": flow_name,
            "embedding_metadata": {
                "file_name": document_name
            }
        }
        
        try:
            # Make the API request
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the response
            extraction_data = response.json()
            response_text = extraction_data.get("response", "")
            
            # Process the extracted data
            processed_data = self._process_extracted_text(response_text)
            return processed_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error extracting data from NIA policy: {str(e)}")
            return {
                "insurer": "NIA",
                "error": str(e),
                "basicInfo": {},
                "coverages": {},
                "addOns": {},
                "excess": {},
                "sumInsured": {},
                "premium": {},
                "specialConditions": {}
            }
    
    def _process_extracted_text(self, response_text: str) -> Dict[str, Any]:
        """
        Process the extracted text response into structured data.
        
        Args:
            response_text: Raw text response from the API
            
        Returns:
            Structured insurance data
        """
        processed_data = {
            "insurer": "NIA",
            "basicInfo": {},
            "coverages": {},
            "addOns": {},
            "excess": {},
            "sumInsured": {},
            "premium": {},
            "specialConditions": {}
        }
        
        # Map for basic policy information extraction
        basic_info_mapping = {
            'Insured/Principal Name': ['Insured Name:', 'NAME & ADDRESS OF THE PRINCIPAL', 'Principal Name:', 'Principal:'],
            'Contractor Name': ['Contractor Name:', 'NAME & ADDRESS OF THE CONTRACTOR', 'Contractor:'],
            'GSTIN': ['GSTIN:', 'GSTIN'],
            'Job Number': ['Job Number:', 'JOB NUMBER', 'Project Code:', 'Job No.:'],
            'Job Description': ['Job Description:', 'JOB DESCRIPTION', 'Project Description:'],
            'Scope': ['Scope:', 'SCOPE', 'Scope of Work:', 'Scope of works include:'],
            'Location': ['Location:', 'LOCATION', 'Risk Location:', 'Site Location:'],
            'Project Period': ['Project Period:', 'PROJECT PERIOD', 'Policy Period:'],
            'Extended Maintenance': ['Extended Maintenance Cover:', 'EXTENDED MAINTENANCE COVER', 'Maintenance Period:']
        }
        
        # Extract basic policy information
        for key, possible_labels in basic_info_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
                # Try to find the value using various patterns
                for pattern_str in [
                    f"{label}[\\s\\:\\-]+(.*?)(?=[\\n\\r]|$)",
                    f"{label}[\\s\\:\\-]+([\\d\\,\\.\\s]+)",
                    f"\\b{label}\\b[\\s\\:\\-]+([^\\n]+)",
                    f"^{label}\\s*([^\\n]+)$"
                ]:
                    import re
                    pattern = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
                    match = pattern.search(response_text)
                    if match and match.group(1) and match.group(1).strip():
                        value = match.group(1).strip()
                        break
                
                if value != 'Not Found':
                    break
            
            processed_data["basicInfo"][key] = value
        
        # Map for excess/deductible information extraction
        excess_mapping = {
            'Normal Period Claims': ['EXCESS FOR NORMAL PERIOD CLAIMS', 'Normal Period Claims:', 'Normal Period Claims'],
            'Maintenance/AOG Claims': ['EXCESS FOR MAINTENANCE PERIOD CLAIMS/AOG /MAJOR PERILS', 'Maintenance Period Claims:', 'AOG Claims:'],
            'Design Defects': ['EXCESS FOR DESIGN DEFECTS COVER DE-3', 'Design Defects Cover:', 'Design Defect Excess:'],
            'Terrorism': ['EXCESS FOR TERRORISM', 'Terrorism Excess:', 'Terrorism:'],
            'Glass': ['EXCESS FOR GLASS', 'Glass Excess:', 'Glass:']
        }
        
        # Extract excess/deductible information
        for key, possible_labels in excess_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
                import re
                pattern = re.compile(f"{label}[\\s\\:\\-]+([^\\n]+)", re.IGNORECASE)
                match = pattern.search(response_text)
                if match and match.group(1) and match.group(1).strip():
                    value = match.group(1).strip()
                    break
            
            processed_data["excess"][key] = value
        
        # Map for sum insured breakup
        sum_insured_mapping = {
            'Contract Price': ['Contract Price', 'Contract Price of', 'Contract Value:'],
            'Additional Sum': ['Additional sum to cover', 'Additional sum', 'Additional exposure:'],
            'Materials by Principal': ['Materials or items supplied by the Principal', 'Principal Materials:', 'Principal Supplied Materials:'],
            'Temporary Works': ['All kind of temporary works', 'Temporary works:', 'Temporary structures:'],
            'Office Furniture': ['Office furniture, fixtures', 'Office equipment:', 'Furniture & fixtures:'],
            'Contractor Materials': ['Contractor\'s own materials', 'Contractor materials:', 'Contractor consumables:'],
            'Tools & Tackles': ['Contractor\'s Tools & tackles', 'Tools & tackles:', 'Small tools:'],
            'Total Project Value': ['TOTAL PROJECT VALUE', 'Total Sum Insured:', 'Total Project Value:']
        }
        
        # Extract sum insured breakup
        for key, possible_labels in sum_insured_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
                import re
                pattern = re.compile(f"{label}[\\s\\:\\-]*([^\\n]+)", re.IGNORECASE)
                match = pattern.search(response_text)
                if match and match.group(1) and match.group(1).strip():
                    value = match.group(1).strip()
                    break
            
            processed_data["sumInsured"][key] = value
        
        # Map for add-on covers
        add_on_mapping = {
            'Extended Maintenance': ['EXTENDED MAINTENANCE COVER', 'Extended Maintenance Cover:', 'Maintenance Period:'],
            'Debris Removal': ['CLEARANCE & REMOVAL OF DEBRIS', 'Debris Removal:', 'Removal of Debris:'],
            'Third Party Liability': ['THIRD PARTY LIABILITY', 'TPL:', 'Third Party:'],
            'Escalation': ['ESCALATION', 'Escalation:', 'Escalation limit:'],
            'Earthquake': ['EARTHQUAKE', 'Earthquake Zone:', 'EQ Cover:'],
            'Waiver of Subrogation': ['WAIVER OF SUBROGATION', 'Waiver of Subrogation:', 'Subrogation waiver:'],
            'Design Defect': ['DESIGN DEFECT', 'Design Defect Cover:', 'DE3 Cover:'],
            'Owners Surrounding Property': ['OWNERS SURROUNDING PROPERTY', 'Surrounding Property:', 'OSP Cover:'],
            'Offsite Storage': ['COVER FOR OFFSITE STORAGE', 'Offsite Storage:', 'Storage Cover:'],
            'Internal Shifting': ['COVER FOR INTERNAL SHIFTING', 'Internal Shifting:', 'Shifting Cover:'],
            'Plans and Documents': ['PLANS AND DOCUMENTS', 'Plans & Documents:', 'Document Cover:'],
            'Put to Use': ['PUT TO USE', 'Put to Use Clause:', 'PtU Cover:'],
            'Multiple Insured': ['MULTIPLE INSURED CLAUSE', 'Multiple Insured:', 'Multiple Insureds:'],
            'Principal & Contractor': ['PRINCIPAL & CONTRACTOR', 'Principal as Insured:', 'Named Insureds:'],
            '50/50 Clause': ['50 / 50 CLAUSE', '50/50 Clause:', '50:50 Clause:'],
            '72 Hours Clause': ['72 HRS CLAUSE', '72 Hours Clause:', '72hr Clause:'],
            'Free Reinstatement': ['FREE AUTOMATIC RE-INSTATEMENT', 'Reinstatement:', 'Auto Reinstatement:'],
            'Professional Fees': ['PROFESSIONAL FEES', 'Professional Fees:', 'Prof Fees:'],
            'Contribution Clause': ['WAIVER OF CONTRIBUTION CLAUSE', 'Contribution Waiver:', 'Non-Contribution:'],
            'Custom Duty': ['ADDITIONAL CUSTOM DUTY', 'Custom Duty:', 'Duty Cover:'],
            'Expediting Cost': ['EXPEDITING COST', 'Air Freight:', 'Express Freight:'],
            'Loss Minimisation': ['LOSS MINIMISATION EXPENSES', 'Loss Minimization:', 'Loss Min:'],
            'Co-Insurance': ['CO-INSURANCE CLAUSE', 'Co-Insurance:', 'Coinsurance:'],
            'Breakage of Glass': ['BREAKAGE OF GLASS', 'Glass Cover:', 'Glass:'],
            'Cessation of Works': ['CESSATION OF WORKS', 'Cessation:', 'Works Cessation:'],
            'Claim Preparation': ['CLAIM PREPARATION COST', 'Claim Prep:', 'Preparation Costs:'],
            'Terrorism': ['TERRORISM', 'Terrorism Cover:', 'RSMD:'],
            'Public Authorities': ['PUBLIC AUTHORITIES CLAUSE', 'Public Auth:', 'Authorities:'],
            'Temporary Repair': ['TEMPORARY REPAIR CLAUSE', 'Temp Repair:', 'Emergency Repairs:'],
            'Improvement Cost': ['IMPROVEMENT COST', 'Improvement:', 'Betterment:']
        }
        
        # Extract add-on covers
        for key, possible_labels in add_on_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
                import re
                # Try to find the labeled item in the document
                pattern = re.compile(f"{label}[\\s\\:\\-]*([^\\n]+)", re.IGNORECASE)
                match = pattern.search(response_text)
                if match and match.group(1) and match.group(1).strip():
                    value = match.group(1).strip()
                    break
                    
                # Try to find as an add-on cover item
                addon_pattern = re.compile(f"[0-9]+\\s*{label}\\s*([^\\n]+)", re.IGNORECASE)
                addon_match = addon_pattern.search(response_text)
                if addon_match and addon_match.group(1) and addon_match.group(1).strip():
                    value = addon_match.group(1).strip()
                    break
            
            # If not found with value, check if it's just included
            if value == 'Not Found':
                for label in possible_labels:
                    import re
                    included_pattern = re.compile(f"[0-9]+\\s*{label}", re.IGNORECASE)
                    if included_pattern.search(response_text):
                        value = 'Included'
                        break
            
            processed_data["addOns"][key] = value
        
        # Map for premium information
        premium_mapping = {
            'Building Type': ['RATED AS', 'Building Type:', 'Structure Type:'],
            'CAR Premium': ['CAR', 'Base Premium:', 'CAR Premium:'],
            'Earthquake Premium': ['EARTHQUAKE', 'EQ Premium:', 'Earthquake:'],
            'STFI Premium': ['STFI', 'STFI Premium:', 'STFI:'],
            'Breakage of Glass Premium': ['BREAKAGE OF GLASS', 'Glass Premium:', 'Glass:'],
            'Premium Including EQ & STFI': ['PREMIUM INCL EQ & STFI', 'Total Premium before GST:', 'Net Premium:'],
            'GST': ['GST @', 'GST Amount:', 'Tax:'],
            'Net Premium': ['NET CAR PREMIUM', 'Final Premium:', 'Total Premium:'],
            'Total Premium': ['TOTAL CAR PREMIUM', 'Gross Premium:', 'Premium with GST:']
        }
        
        # Extract premium information
        for key, possible_labels in premium_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
                import re
                # Check premium table format
                table_pattern = re.compile(f"{label}\\s*([^\\n]+)\\s*[0-9\\.]+\\s*([0-9,\\.]+)", re.IGNORECASE)
                table_match = table_pattern.search(response_text)
                if table_match and table_match.group(2) and table_match.group(2).strip():
                    si_value = table_match.group(1).strip() if table_match.group(1) else ''
                    premium_value = table_match.group(2).strip()
                    value = f"{premium_value}" + (f" ({si_value})" if si_value else "")
                    break
                
                # Try direct match
                direct_pattern = re.compile(f"{label}[\\s\\:\\-]*([^\\n]+)", re.IGNORECASE)
                direct_match = direct_pattern.search(response_text)
                if direct_match and direct_match.group(1) and direct_match.group(1).strip():
                    value = direct_match.group(1).strip()
                    break
            
            processed_data["premium"][key] = value
        
        # Extract special conditions and warranties
        import re
        warranties_match = re.search(r"WARRANTIES:\s*([\s\S]*?)(?=NOTE:|$)", response_text, re.IGNORECASE)
        if warranties_match:
            processed_data["specialConditions"]["Warranties"] = warranties_match.group(1).strip()
        
        # Extract endorsements if available
        endorsements_match = re.search(r"Subject to the below endorsements:([\s\S]*?)(?=Page|$)", response_text, re.IGNORECASE)
        if endorsements_match:
            processed_data["specialConditions"]["Endorsements"] = endorsements_match.group(1).strip()
        
        # Look for any other special conditions
        special_conditions_match = re.search(r"Subject to:([\s\S]*?)(?=Page|$)", response_text, re.IGNORECASE)
        if special_conditions_match:
            processed_data["specialConditions"]["Other Conditions"] = special_conditions_match.group(1).strip()
        
        return processed_data
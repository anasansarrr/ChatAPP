import requests
import json
from typing import Dict, Any

class RelianceInsuranceAgent:
    """
    AI agent for extracting insurance information from Reliance policy documents.
    
    This agent connects to the LNT chatservice API to extract structured information
    from Reliance insurance policy documents using AI.
    """
    
    def __init__(self, bearer_token: str, base_url: str = "https://lntcs.ai/chatservice/chat"):
        """
        Initialize the Reliance insurance extraction agent.
        
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
        Create a specialized extraction prompt for Reliance insurance policies.
            
        Returns:
            A detailed prompt for extracting insurance information
        """
        return """
          I need you to carefully extract specific insurance information from the Reliance policy document. 
          Focus ONLY on extracting the exact values for each item listed below.
  
          For each item, provide ONLY the value with no extra explanation:
  
          ## Basic Policy Information
          - Insured Name: [Extract the insured name, e.g., "M/s. Larsen & Toubro Limited"]
          - Principal Name: [Extract the principal name]
          - Contractor Name: [Extract the contractor name]
          - Risk Location: [Extract the exact risk location]
          - Project Code/Job No.: [Extract project code]
          - Policy Period: [Extract policy period in months]
          - Sum Insured: [Extract the total sum insured value]
          - Premium before tax: [Extract premium before tax]
          - GST amount: [Extract GST amount]
          - Final Premium: [Extract final premium amount]
          - Sum Insured: [Extract the sum Insured value]
  
          ## Excess/Deductible Information
          - Normal Claims: [Extract normal claims excess]
          - AOG/Testing Claims: [Extract AOG/Testing claims excess]
          - Special Deductibles: [Extract any special deductibles mentioned]
  
          ## Standard Coverages
          - Basic Premium: [Extract basic premium amount]
          - Earthquake Cover: [Extract earthquake coverage details]
          - STFI: [Extract STFI coverage details]
          - Terrorism: [Extract terrorism coverage details]
          - Marine: [Extract marine coverage details]
          - Total Premium excluding GST: [Extract total premium excluding GST]
          - GST @ 18%: [Extract GST amount or percentage]
          - Total Premium including GST: [Extract total premium including GST]
  
          ## Add-on Covers
          - Escalation: [Extract escalation details]
          - Waiver of Subrogation: [Extract waiver details]
          - Design Defect: [Extract design defect coverage details]
          - Owners Surrounding Property: [Extract details]
          - Cover for Offsite Storage/Fabrication: [Extract details]
          - Plans & Documents/Valuable Documents: [Extract details]
          - Put to Use: [Extract details]
          - Breakage of Glass: [Extract details]
          - Multiple Insured Clause: [Extract details]
          - 50/50 Clause: [Extract details]
          - 72 Hours Clause: [Extract details]
          - Free Automatic Reinstatement: [Extract details]
          - Professional Fees: [Extract details]
          - Waiver of Contribution Clause: [Extract details]
          - Additional Custom Duty: [Extract details]
          - Air Freight & Express Freight: [Extract details]
          - Loss Minimization Expense: [Extract details]
          - TPL with Cross Liability: [Extract details]
          - Debris Removal: [Extract details]
          - Cessation of Works: [Extract details]
          - Claim Preparation Costs: [Extract details]
          - Temporary Repair Clause: [Extract details]
          - Improvement cost of insured property: [Extract details]

          ## Sum Insured Breakup
          - Contract Price: [Extract the contract price]
          - Additional to Cover all such work material in the BOQ: [Extract the detail]
          - All kind of temporary works: [Extract the detail]
          - Extract the whole Table and Total sum insured Value
        """
    
    def extract_data(self, space_name: str, flow_name: str, document_name: str = "Reliance-policy-document.pdf") -> Dict[str, Any]:
        """
        Extract insurance data from Reliance policy document.
        
        Args:
            space_name: The space name for the API
            flow_name: The flow name for the API
            document_name: The name of the document to extract from (optional)
            
        Returns:
            Processed insurance data
        """
        print(f"Extracting data from Reliance policy document: {document_name}...")
        
        extraction_prompt = self.create_extraction_prompt()
        
        # Create request payload
        payload = {
            "query": extraction_prompt,
            "space_name": space_name,
            "userId": "anonymous",
            "hint": "For the Reliance document, look for exact phrases, headings, and tables that contain the insurance details. Pay special attention to sections labeled as \"Add on covers\", \"Special Conditions\", \"Sum Insured Breakup\", \"DEDUCTIBLES\", \"COVERAGE\", and similar headings. Extract verbatim values where available - exact numbers, limits, and conditions as written in the document.",
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
            
            # Parse the respons
            extraction_data = response.json()
            response_text = extraction_data.get("response", "")
            
            # Process the extracted data
            processed_data = self._process_extracted_text(response_text)
            return processed_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error extracting data from Reliance policy: {str(e)}")
            return {
                "insurer": "Reliance",
                "error": str(e),
                "basicInfo": {},
                "coverages": {},
                "addOns": {},
                "excess": {}
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
            "insurer": "Reliance",
            "basicInfo": {},
            "coverages": {},
            "addOns": {},
            "excess": {}
        }
        
        # Map for basic policy information extraction
        basic_info_mapping = {
            'Insured Name': ['Insured Name:', 'Insured Name', 'NAME OF THE INSURED'],
            'Principal Name': ['Principal Name:', 'Principal Name', 'NAME OF THE PRINCIPAL'],
            'Contractor Name': ['Contractor Name:', 'Contractor Name', 'NAME OF THE CONTRACTOR'],
            'Risk Location': ['Risk Location:', 'Risk Location', 'RISK LOCATION'],
            'Project Description': ['Project Description:', 'Project Description', 'PROJECT DESCRIPTION'],
            'Policy Period': ['Policy Period:', 'Policy Period', 'POLICY PERIOD'],
            'Sum Insured': ['Sum Insured:', 'Sum Insured', 'SUM INSURED'],
            'Premium (before tax)': ['Premium before tax:', 'CAR PREMIUM'],
            'GST amount': ['GST amount:', 'GST:', 'ADD : GST @'],
            'Final Premium': ['Final Premium:', 'FINAL PREMIUM PAYABLE']
        }
        
        # Extract basic policy information
        for key, possible_labels in basic_info_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
                # Try to find the value using various patterns
                for pattern_str in [
                    f"{label}[\\s\\:\\-]+(.*?)(?=[\\n\\r]|$)",
                    f"{label}[\\s\\:\\-]+([\\d\\,\\.\\s]+)",
                    f"\\b{label}\\b[\\s\\:\\-]+([^\\n]+)"
                ]:
                    import re
                    pattern = re.compile(pattern_str, re.IGNORECASE)
                    match = pattern.search(response_text)
                    if match and match.group(1) and match.group(1).strip():
                        value = match.group(1).strip()
                        break
                
                if value != 'Not Found':
                    break
            
            processed_data["basicInfo"][key] = value
        
        # Map for excess/deductible information extraction
        excess_mapping = {
            'Normal claims': ['Normal Claims:', 'Normal Perils', 'Normal claims'],
            'AOG/Testing claims': ['AOG/Testing Claims:', 'AOG/Major Perils', 'AOG / Testing claims'],
            'Special deductibles': ['Special Deductibles:', 'Design Defect :', 'Maintenance period :']
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
        
        # Map for standard coverages
        coverages_mapping = {
            'Basic Premium': ['Basic Premium:', 'Basic Premium', 'CAR PREMIUM'],
            'Earthquake - II': ['Earthquake:', 'Earthquake Cover', 'Earthquake'],
            'STFI': ['STFI:', 'STFI Cover', 'STFI'],
            'Terrorism': ['Terrorism:', 'Terrorism Cover', 'Terrorism'],
            'Marine': ['Marine:', 'Marine Cover', 'Marine'],
            'Total Premium excl GST': ['Total Premium excluding GST:', 'Total Premium excl GST'],
            'GST @ 18%': ['GST @ 18%:', 'ADD : GST @', 'GST amount:'],
            'Total Premium incl GST': ['Total Premium including GST:', 'FINAL PREMIUM PAYABLE']
        }
        
        # Extract standard coverages
        for key, possible_labels in coverages_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
                import re
                pattern = re.compile(f"{label}[\\s\\:\\-]+([^\\n]+)", re.IGNORECASE)
                match = pattern.search(response_text)
                if match and match.group(1) and match.group(1).strip():
                    value = match.group(1).strip()
                    break
            
            # Special handling for coverages that might be in the "COVERAGE" section
            if value == 'Not Found':
                coverage_section_match = re.search(r"COVERAGE(.*?)(?=CLAUSES APPLICABLE|$)", response_text, re.DOTALL | re.IGNORECASE)
                if coverage_section_match:
                    section = coverage_section_match.group(1)
                    clean_key = key.replace(' - II', '')
                    pattern = re.compile(f"{clean_key}\\b.*?(?:Cover)?\\s+(.*?)(?=\\n|$)", re.IGNORECASE)
                    section_match = pattern.search(section)
                    if section_match and section_match.group(1):
                        value = section_match.group(1).strip()
            
            processed_data["coverages"][key] = value
        
        # Map for add-on covers
        add_on_mapping = {
            'Escalation': ['Escalation:', 'Escalation'],
            'Earthquake': ['Earthquake:', 'Earthquake'],
            'Waiver of Subrogation': ['Waiver of Subrogation:', 'Waiver of subrogation'],
            'Design Defect - DE3': ['Design Defect:', 'Design Defect cover', 'Design Defect'],
            'Owners Surrounding property with Flexa': ['Owners surrounding property:', 'Owners surrounding property'],
            'Cover for offsite storage, fabrication': ['Cover for offsite storage/Fabrication:', 'Cover for offsite storage'],
            'Plans & Documents': ['Plans & Documents:', 'Cover for Valuable documents'],
            'Put to Use': ['Put to Use:', 'Put to use clause'],
            'Breakage of glass': ['Breakage of Glass:', 'Breakage of glass'],
            'Multiple Insured Clause': ['Multiple Insured Clause:', 'Multiple insured clause'],
            '50/50 Clause': ['50/50 Clause:', '50 : 50 Clause'],
            '72 Hours Clause': ['72 Hours Clause:', '72 Hours Clause'],
            'Free Auto. Reinstatement upto 10%': ['Free Automatic Reinstatement:', 'Free Automatic Reinstatement of SI'],
            'Professional Fees': ['Professional Fees:', 'Professional Fees'],
            'Waiver of contribution clause': ['Waiver of Contribution Clause:', 'Waiver of Contribution'],
            'Additional custom duty - upto 10 Cr': ['Additional Custom Duty:', 'Additional Custom Duty', 'Aditional Customs Duty'],
            'Air freight & exp freight upto 30% claim': ['Air Freight & Express Freight:', 'Expediting cost including Air'],
            'Loss Minimisation Expense': ['Loss Minimization Expense:', 'Loss Minimization expenses'],
            'TPL with Cross Liability': ['TPL with Cross Liability:', 'Third Party Libaility including Cross Liability'],
            'Debris Removal (Incl Foreign)': ['Debris Removal:', 'Debris removal'],
            'Cessation of Works': ['Cessation of Works:', 'Cessation of works'],
            'Claim Preparation Costs': ['Claim Preparation Costs:', 'Claim Preparation clause'],
            'Temporary Repair Clause': ['Temporary Repair Clause:', 'Temporary Repair Clause'],
            'Improvement cost actual of insured property': ['Improvement cost:', 'Improvement cost actual']
        }
        
        # Extract add-on covers
        # First check the COVERAGE section
        coverage_section_match = re.search(r"COVERAGE(.*?)(?=CLAUSES APPLICABLE|$)", response_text, re.DOTALL | re.IGNORECASE)
        coverage_section = coverage_section_match.group(1) if coverage_section_match else ""
        
        # Then check the CLAUSES APPLICABLE section
        clauses_section_match = re.search(r"CLAUSES APPLICABLE(.*?)(?=$)", response_text, re.DOTALL | re.IGNORECASE)
        clauses_section = clauses_section_match.group(1) if clauses_section_match else ""
        
        # Combined sections for searching
        combined_sections = coverage_section + "\n" + clauses_section
        
        for key, possible_labels in add_on_mapping.items():
            value = 'Not Found'
            
            # First try to find in the combined sections
            for label in possible_labels:
                import re
                # For coverage section, look for label followed by value/limit
                pattern = re.compile(f"{label}[\\s\\:\\-]+([^\\n]+)", re.IGNORECASE)
                match = pattern.search(combined_sections)
                if match and match.group(1) and match.group(1).strip():
                    value = match.group(1).strip()
                    break
            
            # If not found, look for the key itself in the clauses section
            if value == 'Not Found':
                # Remove anything after a dash or colon
                simplified_key = re.sub(r"\s*[-:].*$", "", key).strip()
                if re.search(r'\b' + re.escape(simplified_key) + r'\b', combined_sections, re.IGNORECASE):
                    value = 'Included'
            
            processed_data["addOns"][key] = value
        
        return processed_data
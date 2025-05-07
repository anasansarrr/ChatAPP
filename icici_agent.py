import requests
import json
from typing import Dict, Any

class ICICIInsuranceAgent:
    """
    AI agent for extracting insurance information from ICICI policy documents.
    
    This agent connects to the LNT chatservice API to extract structured information
    from ICICI insurance policy documents using AI.
    """
    
    def __init__(self, bearer_token: str, base_url: str = "https://lntcs.ai/chatservice/chat"):
        """
        Initialize the ICICI insurance extraction agent.
        
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
        Create a specialized extraction prompt for ICICI insurance policies.
            
        Returns:
            A detailed prompt for extracting insurance information
        """
        return """
          I need you to carefully extract specific insurance information from the ICICI policy document. 
          Focus ONLY on extracting the exact values for each item listed below.
  
          For each item, provide ONLY the value with no extra explanation:
  
          ## Basic Policy Information
          - Insured Name: [Extract the insured name, e.g., "M/s. The Peerless General Finance & Investment Co. Ltd"]
          - Principal Name: [Extract the principal name]
          - Contractor Name: [Extract the contractor name, e.g., "M/s. Larsen & Toubro Limited"]
          - Risk Location: [Extract the exact risk location]
          - Project Code/Job No.: [Extract project code"]
          - Policy Period: [Extract policy period in months,"]
          - Sum Insured: [Extract the total sum insured value"]
          - Premium before tax: [Extract premium before tax"]
          - GST amount: [Extract GST amount"]
          - Final Premium: [Extract final premium amount"]
          -Sum Insured :["Extract the sum Insured value" ]
  
          ## Excess/Deductible Information
          - Normal Claims: [Extract normal claims excess"]
          - AOG/Testing Claims: [Extract AOG/Testing claims excess"]
          - Special Deductibles: [Extract any special deductibles mentioned]
  
          ## Standard Coverages
          - Basic Premium: [Extract basic premium amount]
          - Earthquake Cover: [Extract earthquake coverage details"]
          - STFI: [Extract STFI coverage details"]
          - Terrorism: [Extract terrorism coverage details]
          - Marine: [Extract marine coverage details]
          - Total Premium excluding GST: [Extract total premium excluding GST]
          - GST @ 18%: [Extract GST amount or percentage]
          - Total Premium including GST: [Extract total premium including GST]
  
          ## Add-on Covers
          - Escalation: [Extract escalation details, ]
          - Waiver of Subrogation: [Extract waiver details]
          - Design Defect: [Extract design defect coverage details"]
          - Owners Surrounding Property: [Extract details"]
          - Cover for Offsite Storage/Fabrication: [Extract details]
          - Plans & Documents/Valuable Documents: [Extract detail"]
          - Put to Use: [Extract details]
          - Breakage of Glass: [Extract details, ]
          - Multiple Insured Clause: [Extract details]
          - 50/50 Clause: [Extract details]
          - 72 Hours Clause: [Extract details]
          - Free Automatic Reinstatement: [Extract details"]
          - Professional Fees: [Extract details]
          - Waiver of Contribution Clause: [Extract details]
          - Additional Custom Duty: [Extract details]
          - Air Freight & Express Freight: [Extract details]
          - Loss Minimization Expense: [Extract details]
          - TPL with Cross Liability: [Extract details"]
          - Debris Removal: [Extract details "]
          - Cessation of Works: [Extract details"]
          - Claim Preparation Costs: [Extract details]
          - Temporary Repair Clause: [Extract details ]
          - Improvement cost of insured property: [Extract details"]

          ## Sum Insured Breakup
          -Contract Price:["extract the contract price"]
          -Additional to Cover all such work material in the BOQ.["Extract the detail"]
          - All kind of temproary works ["Extract the detail"] 
          - Extract the whole Table and Total sum insured Value
        """
    
    def extract_data(self, space_name: str, flow_name: str, document_name: str = "Terms-LE23M976_-ICICI.pdf") -> Dict[str, Any]:
        """
        Extract insurance data from ICICI policy document.
        
        Args:
            space_name: The space name for the API
            flow_name: The flow name for the API
            document_name: The name of the document to extract from (optional)
            
        Returns:
            Processed insurance data
        """
        print("Extracting data from ICICI policy document...")
        
        extraction_prompt = self.create_extraction_prompt()
        
        # Create request payload
        payload = {
            "query": extraction_prompt,
            "space_name": space_name,
            "userId": "anonymous",
            "hint": "For the ICICI document, look for exact phrases, headings, and tables that contain the insurance details. Pay special attention to sections labeled as \"Add on covers\", \"Special Conditions\", \"Sum Insured Breakup\", and similar headings. Extract verbatim values where available - exact numbers, limits, and conditions as written in the document.",
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
            print(f"Error extracting data from ICICI policy: {str(e)}")
            return {
                "insurer": "ICICI",
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
            "insurer": "ICICI",
            "basicInfo": {},
            "coverages": {},
            "addOns": {},
            "excess": {}
        }
        
        # Map for basic policy information extraction
        basic_info_mapping = {
            'Insured Name': ['Insured Name:', 'Insured Name'],
            'Principal Name': ['Principal Name:', 'Principal Name', 'Name of Principal:'],
            'Contractor Name': ['Contractor Name:', 'Contractor Name', 'Name of Contractor:'],
            'Risk Location': ['Risk Location:', 'Risk Location'],
            'Project Description': ['Project Description:', 'Project Description', 'Scope of Work:', 'Nature of Project:'],
            'Policy Period': ['Policy Period:', 'Policy Period', 'Tentative Policy Period:'],
            'Sum Insured': ['Sum Insured:', 'Sum Insured', 'Total Sum Insured:'],
            'Premium (before tax)': ['Premium before tax:', 'Premium Before Service Tax:', 'Final Premium Before Service Tax:'],
            'GST amount': ['GST amount:', 'GST:', 'GST @'],
            'Final Premium': ['Final Premium:', 'Final premium:', 'Final Premium']
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
            'Normal claims': ['Normal Claims:', 'Normal claims', 'Normal:', 'Normal Claims -'],
            'AOG/Testing claims': ['AOG/Testing Claims:', 'AOG/Testing claims', 'AOG / Testing claims'],
            'Special deductibles': ['Special Deductibles:', 'Special deductibles', 'Excess on glass items']
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
            'Basic Premium': ['Basic Premium:', 'Basic Premium'],
            'Earthquake - II': ['Earthquake Cover:', 'Earthquake Cover', 'Earthquake Coverage', 'Earthquake Cover \\(Fire & Shock\\)'],
            'STFI': ['STFI:', 'STFI', 'STFI Coverage', 'STFI Included'],
            'Terrorism': ['Terrorism:', 'Terrorism', 'Terrorism Coverage', 'End 32 - Terrorism'],
            'Marine': ['Marine:', 'Marine', 'Marine Coverage'],
            'Total Premium excl GST': ['Total Premium excluding GST:', 'Total Premium excl GST', 'Total Premium Before Service Tax'],
            'GST @ 18%': ['GST @ 18%:', 'GST @ 18%', 'GST:'],
            'Total Premium incl GST': ['Total Premium including GST:', 'Total Premium incl GST', 'Final premium']
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
            
            processed_data["coverages"][key] = value
        
        # Map for add-on covers
        add_on_mapping = {
            'Escalation': ['Escalation:', 'Escalation', 'Escalation upto'],
            'Earthquake': ['Earthquake:', 'Earthquake', 'Earthquake Cover'],
            'Waiver of Subrogation': ['Waiver of Subrogation:', 'Waiver of subrogation', 'Waiver of Subrogation'],
            'Design Defect - DE3': ['Design Defect:', 'Design Defect', 'Design Defect -'],
            'Owners Surrounding property with Flexa': ['Owners Surrounding Property:', "Owners' surrounding property", 'Owners Surrounding property'],
            'Cover for offsite storage, fabrication': ['Cover for Offsite Storage/Fabrication:', 'Cover for offsite storage', 'Offsite storage'],
            'Plans & Documents': ['Plans & Documents:', 'Valuable Documents', 'Cover for Valuable Documents'],
            'Put to Use': ['Put to Use:', 'Put to Use', 'Continuity of cover during operational phase'],
            'Breakage of glass': ['Breakage of Glass:', 'Breakage of Glass', 'Breakage of Glass Cover'],
            'Multiple Insured Clause': ['Multiple Insured Clause:', 'Multiple Insured Clause'],
            '50/50 Clause': ['50/50 Clause:', '50:50 Clause', '50/50 Clause'],
            '72 hours clause': ['72 Hours Clause:', '72 Hours Clause'],
            'Free Auto. Reinstatement upto 10%': ['Free Automatic Reinstatement:', 'Free Automatic Re-instatement', 'Free Auto. Reinstatement'],
            'Professional Fees': ['Professional Fees:', 'Professional fees'],
            'Waiver of contribution clause': ['Waiver of Contribution Clause:', 'Waiver of contribution clause'],
            'Additional custom duty - upto 10 Cr': ['Additional Custom Duty:', 'Additional Custom duty'],
            'Air freight & exp freight upto 30% claim': ['Air Freight & Express Freight:', 'Expediting cost', 'air freight & express freight'],
            'Loss Minimisation Expense': ['Loss Minimization Expense:', 'Loss minimisation expenses'],
            'TPL with Cross Liability': ['TPL with Cross Liability:', 'TPL with Cross Liability'],
            'Debris Removal (Incl Foreign)': ['Debris Removal:', 'Debris Removal limit'],
            'Cessation of Works': ['Cessation of Works:', 'Cessation of Works'],
            'Claim Preparation Costs': ['Claim Preparation Costs:', 'Claims preparation Cost'],
            'Temporary Repair Clause': ['Temporary Repair Clause:', 'Temporary Repair Clause'],
            'Improvement cost actual of insured property': ['Improvement cost:', 'Improvement cost actual of insured property']
        }
        
        # Extract add-on covers
        for key, possible_labels in add_on_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
                import re
                pattern = re.compile(f"{label}[\\s\\:\\-]+([^\\n]+)", re.IGNORECASE)
                match = pattern.search(response_text)
                if match and match.group(1) and match.group(1).strip():
                    value = match.group(1).strip()
                    break
            
            # If not found, search for just included/covered
            if value == 'Not Found':
                import re
                simple_pattern = re.compile(f"{key}\\s*(Included|Covered)", re.IGNORECASE)
                simple_match = simple_pattern.search(response_text)
                if simple_match:
                    value = 'Included'
            
            processed_data["addOns"][key] = value
        
        # Additional search for add-on covers in bulleted or listed format
        import re
        add_on_section_match = re.search(r"Add[-\s]on covers:[\s\S]*?(?=Special Conditions|$)", response_text, re.IGNORECASE)
        if add_on_section_match:
            section = add_on_section_match.group(0)
            
            for key in add_on_mapping.keys():
                if processed_data["addOns"][key] == 'Not Found':
                    # Try to find mentions of the add-on in the section
                    key_pattern = re.compile(f"[-\\*•\\s]\\s*({key})\\b([^\\n]*)", re.IGNORECASE)
                    key_match = key_pattern.search(section)
                    
                    if key_match and key_match.group(2):
                        processed_data["addOns"][key] = key_match.group(2).strip() or 'Included'
                    elif key in section:
                        processed_data["addOns"][key] = 'Included'
        
        # Final sweep for any included items that might be in a bullet list
        if 'Add on covers' in response_text or 'Add-on covers' in response_text:
            for key in add_on_mapping.keys():
                if processed_data["addOns"][key] == 'Not Found':
                    # Remove anything after a dash
                    simplified_key = re.sub(r"\s*-.*$", "", key).strip()
                    import re
                    mention_pattern = re.compile(f"[-\\*•\\s]\\s*({simplified_key})\\b", re.IGNORECASE)
                    
                    if mention_pattern.search(response_text):
                        processed_data["addOns"][key] = 'Included'
        
        return processed_data
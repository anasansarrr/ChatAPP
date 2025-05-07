import requests
import json
import re
from typing import Dict, Any

class UIICInsuranceAgent:
    """
    AI agent for extracting insurance information from United India Insurance Co. Ltd (UIIC) policy documents.
    
    This agent connects to the LNT chatservice API to extract structured information
    from UIIC insurance policy documents using AI.
    """
    
    def __init__(self, bearer_token: str, base_url: str = "https://lntcs.ai/chatservice/chat"):
        """
        Initialize the UIIC insurance extraction agent.
        
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
        Create a specialized extraction prompt for UIIC insurance policies.
            
        Returns:
            A detailed prompt for extracting insurance information
        """
        return """
          I need you to carefully extract specific insurance information from the United India Insurance Co. Ltd (UIIC) policy document. 
          Focus ONLY on extracting the exact values for each item listed below.
  
          For each item, provide ONLY the value with no extra explanation:
  
          ## Basic Policy Information
          - Insured Name: [Extract the insured name, e.g., "M/s. Larsen & Toubro Limited"]
          - Principal Name: [Extract the principal name]
          - Contractor Name: [Extract the contractor name]
          - Risk Location: [Extract the exact risk location]
          - Project Code/Job No.: [Extract project code, e.g., "LE23M976"]
          - Project Description: [Extract the project description]
          - Policy Period: [Extract policy period in months, e.g., "36 Months + 12 Months EMP"]
          - Sum Insured: [Extract the total sum insured value]
          - Premium before tax: [Extract premium before tax]
          - GST amount: [Extract GST amount]
          - Final Premium: [Extract final premium amount]
  
          ## Excess/Deductible Information
          - Normal Claims: [Extract normal claims excess]
          - AOG/Testing Claims: [Extract AOG/Testing claims excess]
          - Special Deductibles: [Extract any special deductibles mentioned, such as Design Defect Excess]
  
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
          - Internal Shifting: [Extract details]
          - Public Authorities Clause: [Extract details]

          ## Installment Details
          - Extract the installment breakdown details (premium, GST, total for each installment)
          
          ## Special Conditions and Warranties
          - Extract all special conditions and warranties mentioned in the document
        """
    
    def extract_data(self, space_name: str, flow_name: str, document_name: str = "UnitedIndia-policy-document.pdf") -> Dict[str, Any]:
        """
        Extract insurance data from UIIC policy document.
        
        Args:
            space_name: The space name for the API
            flow_name: The flow name for the API
            document_name: The name of the document to extract from (optional)
            
        Returns:
            Processed insurance data
        """
        print(f"Extracting data from United India Insurance document: {document_name}...")
        
        extraction_prompt = self.create_extraction_prompt()
        
        # Create request payload
        payload = {
            "query": extraction_prompt,
            "space_name": space_name,
            "userId": "anonymous",
            "hint": "For the United India Insurance document, look for exact phrases, headings, and tables that contain the insurance details. Pay special attention to sections labeled as \"Add-ons\", \"CAR EXCESS\", \"Installment Details\", \"Subjectivity\", \"WARRANTIES\", and similar headings. Extract verbatim values where available - exact numbers, limits, and conditions as written in the document. Focus on the tabular format where add-ons and their respective limits are listed.",
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
            print(f"Error extracting data from United India Insurance policy: {str(e)}")
            return {
                "insurer": "United India Insurance",
                "error": str(e),
                "basicInfo": {},
                "coverages": {},
                "addOns": {},
                "excess": {},
                "installments": {},
                "warranties": []
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
            "insurer": "United India Insurance",
            "basicInfo": {},
            "coverages": {},
            "addOns": {},
            "excess": {},
            "installments": {},
            "warranties": []
        }
        
        # Map for basic policy information extraction
        basic_info_mapping = {
            'Insured Name': ['Insured Name:', 'Insured Name', 'Insured'],
            'Principal Name': ['Principal Name:', 'Principal Name', 'Principal'],
            'Contractor Name': ['Contractor Name:', 'Contractor Name', 'Contractor'],
            'Risk Location': ['Risk Location:', 'Risk Location'],
            'Project Code/Job No.': ['Project Code/Job No.:', 'Project Code', 'Job No.', 'JOB No.'],
            'Project Description': ['Project Description:', 'Project Description'],
            'Policy Period': ['Policy Period:', 'Policy Period', 'Project period'],
            'Sum Insured': ['Sum Insured:', 'Sum Insured'],
            'Premium (before tax)': ['Premium before tax:', 'Premium Before Tax', 'Premium'],
            'GST amount': ['GST amount:', 'GST:', 'GST @'],
            'Final Premium': ['Final Premium:', 'Final Premium', 'Premium']
        }
        
        # Extract basic policy information
        for key, possible_labels in basic_info_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
                # Try to find the value using various patterns
                for pattern_str in [
                    f"{label}[\\s\\:\\-]+(.*?)(?=[\\n\\r]|$)",
                    f"{label}[\\s\\:\\-]+([\\d\\,\\.\\s\\+\\-Rs\\/]+)(?=[\\n\\r]|$)",
                    f"\\b{label}\\b[\\s\\:\\-]+([^\\n]+)"
                ]:
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
            'Normal claims': ['Normal Claims:', 'Normal', 'Normal claims'],
            'AOG/Testing claims': ['AOG/Testing Claims:', 'AOG / Major Perils', 'AOG/Testing claims'],
            'Special deductibles': ['Special Deductibles:', 'Design Defect Excess', 'Special deductibles']
        }
        
        # Extract excess/deductible information
        for key, possible_labels in excess_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
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
            'Total Premium excl GST': ['Total Premium excluding GST:', 'Total Premium excl GST', 'Total Premium'],
            'GST @ 18%': ['GST @ 18%:', 'GST @ 18%', 'GST:'],
            'Total Premium incl GST': ['Total Premium including GST:', 'Total Premium incl GST', 'Total']
        }
        
        # Extract standard coverages - for UIIC documents, this might be less structured
        for key, possible_labels in coverages_mapping.items():
            value = 'Not Found'
            
            for label in possible_labels:
                pattern = re.compile(f"{label}[\\s\\:\\-]+([^\\n]+)", re.IGNORECASE)
                match = pattern.search(response_text)
                if match and match.group(1) and match.group(1).strip():
                    value = match.group(1).strip()
                    break
            
            processed_data["coverages"][key] = value
        
        # Extract add-on covers from tabular format typically used in UIIC documents
        add_on_section_match = re.search(r"Add-?\s*ons\s+Limit(.*?)(?=CAR EXCESS|Installment|WARRANTY|$)", response_text, re.DOTALL | re.IGNORECASE)
        
        if add_on_section_match:
            add_on_text = add_on_section_match.group(1)
            
            # Extract add-on name and limit pairs
            add_on_pattern = re.compile(r"^(.*?)(?:\s{2,}|\t)(.*?)$", re.MULTILINE)
            add_on_matches = add_on_pattern.findall(add_on_text)
            
            for add_on_name, add_on_limit in add_on_matches:
                name = add_on_name.strip()
                if name and not name.lower().startswith(('at united', 'united india')):
                    processed_data["addOns"][name] = add_on_limit.strip()
            
            # If the regex pattern didn't work well, try line-by-line parsing
            if len(processed_data["addOns"]) == 0:
                lines = add_on_text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.lower().startswith(('at united', 'united india')):
                        parts = re.split(r'\s{2,}|\t|(?<=\w)\s+(?=Agreed)', line)
                        if len(parts) >= 2:
                            processed_data["addOns"][parts[0].strip()] = parts[1].strip()
        
        # Extract specific add-ons not captured above
        add_on_mapping = {
            'Escalation': ['Escalation upto', 'Escalation'],
            'Earthquake': ['Earthquake', 'EQ'],
            'STFI': ['STFI'],
            'Waiver of Subrogation': ['Waiver Of Subrogation', 'Waiver of subrogation'],
            'Design Defect': ['Design Defect Cover', 'Design Defect'],
            'Owners Surrounding Property': ['Owners Surrounding Property', 'Owners surrounding property'],
            'Cover for Offsite Storage': ['Cover For Offsite Storage', 'Offsite Storage'],
            'Plans & Documents': ['Plans and Documents', 'Plans & Documents'],
            'Put to Use': ['Put To Use', 'Put to use'],
            'Breakage of Glass': ['Breakage of Glass', 'Glass Breakage'],
            'Multiple Insured Clause': ['Multiple Insured Clause'],
            '50/50 Clause': ['50:50 clause', '50/50 clause'],
            '72 Hours Clause': ['72 Hours clause'],
            'Free Automatic Reinstatement': ['Free Automatic Reinstatement'],
            'Professional Fees': ['Professional Fees'],
            'Waiver of Contribution': ['Waiver of contribution'],
            'Additional Custom Duty': ['Additional Custom Duty'],
            'Air Freight & Express Freight': ['Air Freight', 'Express Freight', 'Expediting Cost'],
            'Loss Minimisation Expense': ['Loss Minimisation', 'Loss Minimization'],
            'TPL with Cross Liability': ['Cross Liability', 'TPL with Cross'],
            'Debris Removal': ['Debris Removal', 'Clearance & Removal'],
            'Cessation of Works': ['Cessation of works', 'Cessation of Works'],
            'Claim Preparation Costs': ['Claim Preparation'],
            'Temporary Repair': ['Temporary Repair Clause'],
            'Improvement Cost': ['Improvement Cost'],
            'Internal Shifting': ['Internal Shifting'],
            'Public Authorities': ['Public Authorities']
        }
        
        # Fill in any missing add-ons by direct matching
        for key, possible_labels in add_on_mapping.items():
            if key not in processed_data["addOns"]:
                for label in possible_labels:
                    pattern = re.compile(f"{label}.*?(Agreed.*?)(?=\\n|$)", re.IGNORECASE)
                    match = pattern.search(response_text)
                    if match and match.group(1):
                        processed_data["addOns"][key] = match.group(1).strip()
                        break
        
        # Extract installment details
        installment_section = re.search(r"Installment Details:-.*?(\n.*?\n.*?\n.*?\n.*?Total.*?)(?=\n\n|\Z)", response_text, re.DOTALL)
        if installment_section:
            installment_text = installment_section.group(1)
            
            # Parse premium, GST, and total for each installment
            installment_pattern = re.compile(r"(\d+)[a-z]{2}\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)", re.IGNORECASE)
            installment_matches = installment_pattern.findall(installment_text)
            
            for i, (installment_num, premium, gst, total) in enumerate(installment_matches, 1):
                if installment_num:
                    processed_data["installments"][f"Installment {installment_num}"] = {
                        "Premium": premium.strip(),
                        "GST": gst.strip(),
                        "Total": total.strip()
                    }
            
            # Extract total if available
            total_pattern = re.compile(r"Total\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)", re.IGNORECASE)
            total_match = total_pattern.search(installment_text)
            if total_match:
                processed_data["installments"]["Total"] = {
                    "Premium": total_match.group(1).strip(),
                    "GST": total_match.group(2).strip(),
                    "Total": total_match.group(3).strip()
                }
        
        # Extract warranties
        warranty_section = re.search(r"WARRANTIES\s*:-.*?(?=At United India|$)", response_text, re.DOTALL | re.IGNORECASE)
        if warranty_section:
            warranty_text = warranty_section.group(0)
            
            # Split by numbered warranties
            warranty_pattern = re.compile(r"(\d+)\)\s+(.*?)(?=\d+\)|$)", re.DOTALL)
            warranty_matches = warranty_pattern.findall(warranty_text)
            
            for warranty_num, warranty_content in warranty_matches:
                # Extract the first line as the title, rest as content
                warranty_lines = warranty_content.strip().split('\n', 1)
                title = warranty_lines[0].strip()
                
                if len(warranty_lines) > 1:
                    content = warranty_lines[1].strip()
                else:
                    content = ""
                
                processed_data["warranties"].append({
                    "number": warranty_num,
                    "title": title,
                    "content": content
                })
        
        # If no warranties found with the pattern above, try another approach
        if not processed_data["warranties"]:
            warranty_texts = re.findall(r"(\d+)\)\s+(.*?):-\s+(.*?)(?=\d+\)|$)", response_text, re.DOTALL)
            for warranty_num, warranty_title, warranty_content in warranty_texts:
                processed_data["warranties"].append({
                    "number": warranty_num,
                    "title": warranty_title.strip(),
                    "content": warranty_content.strip()
                })
        
        return processed_data
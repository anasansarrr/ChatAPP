from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from icici_agent import ICICIInsuranceAgent
# Import additional agents here as needed
# from hdfc_agent import HDFCInsuranceAgent
# from tata_agent import TATAInsuranceAgent

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/extract-icici-data', methods=['POST'])
def extract_icici_data():
    """
    API endpoint to extract insurance data from ICICI policy documents.
    
    Expected JSON request body:
    {
        "token": "your_bearer_token",
        "space_name": "Insurance_usecase",
        "flow_name": "Quote-Comp",
        "document_name": "Terms-LE23M976_-ICICI.pdf"
    }
    
    Returns extracted insurance data in JSON format.
    """
    # Get request data
    data = request.json
    token = data.get('token')
    space_name = data.get('space_name', 'Insurance_usecase')
    flow_name = data.get('flow_name', 'Quote-Comp')
    document_name = data.get('document_name', 'Terms-LE23M976_-ICICI.pdf')
    
    # Validate token
    if not token:
        return jsonify({
            'error': 'Bearer token is required'
        }), 400
    
    try:
        # Create the agent
        agent = ICICIInsuranceAgent(token)
        
        # Extract data from ICICI policy
        result = agent.extract_data(space_name, flow_name)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Error extracting ICICI insurance data: {str(e)}'
        }), 500

@app.route('/extract-insurance-data', methods=['POST'])
def extract_insurance_data():
    """
    Generic API endpoint to extract insurance data from policy documents.
    
    Expected JSON request body:
    {
        "token": "your_bearer_token",
        "insurer": "ICICI", // or "HDFC", "TATA", etc.
        "space_name": "Insurance_usecase",
        "flow_name": "Quote-Comp",
        "document_name": "document.pdf"
    }
    
    Returns extracted insurance data in JSON format.
    """
    # Get request data
    data = request.json
    token = data.get('token')
    insurer = data.get('insurer')
    space_name = data.get('space_name', 'Insurance_usecase')
    flow_name = data.get('flow_name', 'Quote-Comp')
    document_name = data.get('document_name')
    
    # Validate required fields
    if not token:
        return jsonify({'error': 'Bearer token is required'}), 400
    if not insurer:
        return jsonify({'error': 'Insurer type is required'}), 400
    if not document_name:
        return jsonify({'error': 'Document name is required'}), 400
    
    try:
        # Create the appropriate agent based on insurer
        agent = None
        if insurer.upper() == 'ICICI':
            agent = ICICIInsuranceAgent(token)
        # Add more insurers as needed
        # elif insurer.upper() == 'HDFC':
        #     agent = HDFCInsuranceAgent(token)
        # elif insurer.upper() == 'TATA':
        #     agent = TATAInsuranceAgent(token)
        else:
            return jsonify({
                'error': f'Unsupported insurer: {insurer}'
            }), 400
        
        # Extract data from the policy document
        result = agent.extract_data(space_name, flow_name)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Error extracting {insurer} insurance data: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({
        'status': 'ok',
        'message': 'Insurance Extraction Agent API is running'
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)
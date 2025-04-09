import React, { useState, useRef, useEffect } from 'react';
import './App.css';

const ChatApplication = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Fixed values for the API call
  const spaceNameValue = "Insurance_usecase";

  // Get bearer token from CanvasAI
  const bearerToken = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIyNzJza204SEFYVEl1MWgwNThyZUliVVJILWhLTEE5OElFOHdqMDlyXzJNIn0.eyJleHAiOjE3NDEwNzM1ODMsImlhdCI6MTc0MTA3MjA4MywiYXV0aF90aW1lIjoxNzQxMDY5MTkyLCJqdGkiOiI2NzEyYjFhNy1mMzBmLTQyMmQtOTFhNS1hY2VjMzFjMWE4MzYiLCJpc3MiOiJodHRwczovL2xudGNzLmFpL2tleWNsb2FrL3JlYWxtcy9jYW52YXNhaSIsImF1ZCI6ImJyb2tlciIsInN1YiI6ImQwNTkxZDg4LWUyYTEtNGE1OC1hODYxLWNiMTRjZTQ3NjJiZiIsInR5cCI6IkJlYXJlciIsImF6cCI6ImNhbnZhc2FpLWNvbnRyb2xwbGFuZS11aSIsIm5vbmNlIjoiODNhZDZiNWYtNDY4NC00NTA2LThhNGQtZmU2MmJjNjI5ZjYxIiwic2Vzc2lvbl9zdGF0ZSI6IjhhMjBmN2FjLWUyOTgtNDg4Ni1iMjZhLWVjNmE5NWNmNjE3ZCIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiKiIsImh0dHBzOi8vbG50Y3MuYWkvc3R1ZGlvIl0sInJlc291cmNlX2FjY2VzcyI6eyJicm9rZXIiOnsicm9sZXMiOlsicmVhZC10b2tlbiJdfX0sInNjb3BlIjoib3BlbmlkIGVtYWlsIEdyb3VwU2NvcGUgcHJvZmlsZSIsInNpZCI6IjhhMjBmN2FjLWUyOTgtNDg4Ni1iMjZhLWVjNmE5NWNmNjE3ZCIsInVwbiI6ImVmZDI4MWFhLTUyM2EtNDhjNS1iZjY3LWE5ZmQzYTQ4ZmZiYiIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoiQW5hcyBTYWhlYiIsImdyb3VwcyI6WyIvY2FudmFzYWktYWRtaW4iLCIvY2FudmFzYWktY3JlYXRvciJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJlZmQyODFhYS01MjNhLTQ4YzUtYmY2Ny1hOWZkM2E0OGZmYmIiLCJnaXZlbl9uYW1lIjoiQW5hcyIsImZhbWlseV9uYW1lIjoiU2FoZWIiLCJlbWFpbCI6ImFuYXMuc2FoZWItY250QGxudGVjYy5jb20ifQ.OgbldflbcGQdrUC-cYw3sRUQDxpvSY4oLtRhOwguC5PlCHgF04Kw7u6WMD0fVGdfqT2IVdbdhmffhptsp7F9WsxXwB2Ryiygwyg4kEwEuwyFcMvI4r1ByQWCCxCiVmTeGYtWzdmmfabti8Q0NppOkya2Z6WP_BLLypj3tKdJRCuLjWsSsk1lhnKSM_FXBu0t-lxw8a5_XBzFrjmLezFbu2vK7QMomMH2jUCCNHGY9Cd7wSCwUMEjojXmQWZcksInD8CiZJmz6jD9-_71TtxloVwDaQKUmcYv1O-fjTQPns-RcSkSquUAucZlvpjkFP-fVGT3tnEcdenBaE5VVF-C5Q";
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    // Add user message to chat
    const userMessage = { type: 'user', content: query };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('https://lntcs.ai/chatservice/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${bearerToken}`,
          'accept': 'application/json'
        },
        body: JSON.stringify({
          query: query,
          space_name: spaceNameValue,
          userId: "anonymous", // Replace with a default value instead of userProfile
          hint: "Act as an expert attorney specializing in insurance clauses for large-scale construction projects. You have extensive experience in analyzing tender documents and policy documents to extract relevant insurance obligations.Instructions:Extract clauses only related to the above categories.The extracted text should be directly from the tender or policy document.If summarization is needed!, provide a context-based summarization without altering the legal meaning.",
          //flow_name: "clause_generation",  // Added flow_name parameter
          //embedding_metadata: {            // Added embedding_metadata parameter
          //  "file_name": "Proposal_Form_by_Ins_Dept.pdf"
          //}
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Add bot response to chat with source information
      const botMessage = { 
        type: 'bot', 
        content: data.response,
        sources: data.source // Store source information if available
      };
      
      setMessages(prevMessages => [...prevMessages, botMessage]);
      setQuery('');
    } catch (err) {
      setError(err.message);
      console.error("API Error:", err);
      
      // Add error message to chat
      const errorMessage = { 
        type: 'error', 
        content: `Sorry, I encountered an error: ${err.message}` 
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleReturn = () => {
    // Redirect back to the original app (adjust URL as needed)
    window.location.href = "https://lntcs.ai/app";
  };

  // Message formatting functions
  const formatMessage = (message) => {
    if (!message || !message.content) return null;
    
    const content = message.content;
    
    // Check if the content contains table data
    const hasTable = detectTableInText(content);
    
    // Render the content
    const formattedContent = hasTable 
      ? renderFormattedTable(content) 
      : formatRegularText(content);
    
    // Render source documents if they exist
    const sourcesContent = message.sources ? renderSourceDocuments(message.sources) : null;
    
    return (
      <div className="message-full-content">
        <div className="message-content">
          {formattedContent}
        </div>
        {sourcesContent}
      </div>
    );
  };

  // New function to render source documents
  const renderSourceDocuments = (sources) => {
    if (!sources || Object.keys(sources).length === 0) return null;
    
    return (
      <div className="source-documents">
        <h4 className="sources-title">Sources:</h4>
        <ul className="sources-list">
          {Object.entries(sources).map(([key, value], index) => (
            <li key={index} className="source-item">
              <strong>{key}:</strong> {typeof value === 'object' ? JSON.stringify(value) : value}
            </li>
          ))}
        </ul>
      </div>
    );
  };

  const detectTableInText = (text) => {
    // Check for markdown tables
    if (text.includes('|') && text.split('\n').some(line => line.includes('|'))) {
      return true;
    }
    
    // Check for CSV-like data
    const lines = text.split('\n').filter(line => line.trim());
    if (lines.length >= 2) {
      // Check if multiple lines have the same number of delimiters (comma, tab, or multiple spaces)
      const firstLineItems = lines[0].split(/[,\t]|\s{2,}/).filter(item => item.trim());
      const secondLineItems = lines[1].split(/[,\t]|\s{2,}/).filter(item => item.trim());
      
      if (firstLineItems.length >= 2 && firstLineItems.length === secondLineItems.length) {
        // Check if at least one line has numeric content
        return lines.some(line => 
          line.split(/[,\t]|\s{2,}/).some(item => /^\d+(\.\d+)?$/.test(item.trim()))
        );
      }
    }
    
    return false;
  };

  const renderFormattedTable = (text) => {
    // Split into lines and remove empty ones
    const lines = text.split('\n').filter(line => line.trim());
    
    // Handle markdown tables
    if (text.includes('|')) {
      return renderMarkdownTable(lines);
    }
    
    // Handle CSV or space-separated tables
    return renderDelimitedTable(lines);
  };

  const renderMarkdownTable = (lines) => {
    // Extract table lines
    const tableLines = lines.filter(line => line.includes('|'));
    const textBeforeTable = lines.slice(0, lines.indexOf(tableLines[0])).join('\n');
    
    // Extract headers
    const headerLine = tableLines[0];
    let headers = headerLine
      .split('|')
      .map(h => h.trim())
      .filter(h => h !== '');
    
    // Skip separator line if present
    const separatorIndex = tableLines.findIndex(line => 
      line.includes('|') && line.replace(/\|/g, '').trim().replace(/[^-:]/g, '') === line.replace(/\|/g, '').trim()
    );
    
    const dataStartIndex = separatorIndex > 0 ? separatorIndex + 1 : 1;
    
    // Extract data rows
    const rows = tableLines.slice(dataStartIndex).map(line => 
      line.split('|')
        .map(cell => cell.trim())
        .filter(cell => cell !== '')
    );
    
    return (
      <div>
        {textBeforeTable && <div className="text-before-table">{textBeforeTable}</div>}
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                {headers.map((header, index) => (
                  <th key={index}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex}>
                      {isNaN(Number(cell)) ? cell : Number(cell).toLocaleString()}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderDelimitedTable = (lines) => {
    // Determine delimiter
    let delimiter = /,/;
    if (lines[0].includes('\t')) {
      delimiter = /\t/;
    } else if (!lines[0].includes(',') && lines[0].match(/\s{2,}/)) {
      delimiter = /\s{2,}/;
    }
    
    // Extract headers and data
    const headers = lines[0].split(delimiter).map(h => h.trim());
    const rows = lines.slice(1).map(line => 
      line.split(delimiter).map(cell => cell.trim())
    );
    
    return (
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              {headers.map((header, index) => (
                <th key={index}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex}>
                    {isNaN(Number(cell)) ? cell : Number(cell).toLocaleString()}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const formatRegularText = (text) => {
    // Process text with better markdown handling
    const paragraphs = text.split('\n');
    
    // Track if we're in a code block or list
    let inCodeBlock = false;
    let currentCodeContent = '';
    let formattedContent = [];
    
    paragraphs.forEach((paragraph, idx) => {
      // Handle code blocks
      if (paragraph.startsWith('```') || inCodeBlock) {
        if (paragraph.startsWith('```')) {
          if (inCodeBlock) {
            // End of code block
            formattedContent.push(
              <pre key={`code-${idx}`} className="code-block">
                <code>{currentCodeContent}</code>
              </pre>
            );
            currentCodeContent = '';
            inCodeBlock = false;
          } else {
            // Start of code block
            inCodeBlock = true;
          }
        } else if (inCodeBlock) {
          // Content inside code block
          currentCodeContent += paragraph + '\n';
        }
        return;
      }
      
      // Handle bullet points
      if (paragraph.trim().startsWith('- ') || paragraph.trim().startsWith('* ')) {
        formattedContent.push(
          <ul key={`ul-${idx}`} className="bullet-list">
            <li>{paragraph.trim().substring(2)}</li>
          </ul>
        );
        return;
      }
      
      // Handle numbered lists
      if (/^\d+\.\s/.test(paragraph.trim())) {
        formattedContent.push(
          <ol key={`ol-${idx}`} className="numbered-list">
            <li>{paragraph.trim().replace(/^\d+\.\s/, '')}</li>
          </ol>
        );
        return;
      }
      
      // Handle headings
      if (paragraph.startsWith('# ')) {
        formattedContent.push(<h1 key={`h1-${idx}`} className="heading-1">{paragraph.substring(2)}</h1>);
        return;
      }
      
      if (paragraph.startsWith('## ')) {
        formattedContent.push(<h2 key={`h2-${idx}`} className="heading-2">{paragraph.substring(3)}</h2>);
        return;
      }
      
      if (paragraph.startsWith('### ')) {
        formattedContent.push(<h3 key={`h3-${idx}`} className="heading-3">{paragraph.substring(4)}</h3>);
        return;
      }
      
      // Handle bold and italic text
      if (paragraph.trim()) {
        // Replace **bold** with <strong>bold</strong>
        let processedText = paragraph;
        processedText = processedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Replace *italic* with <em>italic</em>
        processedText = processedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        formattedContent.push(
          <p 
            key={`p-${idx}`} 
            dangerouslySetInnerHTML={{ __html: processedText }} 
            className="paragraph"
          />
        );
      } else if (paragraph === '') {
        // Add spacing for empty lines
        formattedContent.push(<div key={`space-${idx}`} className="spacer"></div>);
      }
    });
    
    // Handle any remaining code block content
    if (inCodeBlock && currentCodeContent) {
      formattedContent.push(
        <pre key="code-final" className="code-block">
          <code>{currentCodeContent}</code>
        </pre>
      );
    }
    
    return <div>{formattedContent}</div>;
  };

  return (
    <div className="chat-application">
      <div className="chat-header">
        <div className="header-content">
          <div className="header-logo">
            <span className="logo-icon">AI</span>
          </div>
          <h1 className="header-title">LnTCS AI Assistant</h1>
        </div>
        <div className="user-profile">
          <span className="username">Guest</span>
          <button onClick={handleReturn} className="return-button">Return to App</button>
        </div>
      </div>
      
      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <h2>Welcome to LnTCS AI Assistant</h2>
              <p>Ask me questions about insurance clauses for construction projects!</p>
              <div className="example-queries">
                <p>Try asking:</p>
                <ul>
                  <li>Extract insurance coverage requirements from the proposal</li>
                  <li>What are the liability insurance clauses mentioned?</li>
                  <li>Summarize indemnity clauses in the document</li>
                </ul>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div 
                key={index} 
                className={`message ${message.type}-message`}
              >
                <div className="message-avatar">
                  {message.type === 'user' ? '👤' : message.type === 'bot' ? '🤖' : '⚠️'}
                </div>
                <div className="message-bubble">
                  {formatMessage(message)}
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="message bot-message">
              <div className="message-avatar">🤖</div>
              <div className="message-bubble">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <form onSubmit={handleSubmit} className="chat-input-container">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type your query about insurance clauses..."
            disabled={loading}
            className="chat-input"
          />
          <button 
            type="submit" 
            disabled={loading || !query.trim()} 
            className="chat-submit-button"
            aria-label="Send message"
          >
            <span className="submit-icon">→</span>
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatApplication;
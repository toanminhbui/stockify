'use client'
import React, { ChangeEvent, useState } from "react";
import { Textarea } from "@/components/ui/textarea";

interface Stock {
    s: string;
    n: string;
    t: string;
}

interface ApiResponse {
    data: Stock[];
}

interface StockAnalysis {
    symbol: string,
    current_price: number,
    price_change: number,
    percent_change: number,
    analysis: string,
    market_sentiment: string,
    
}
export default function SearchBar() {
  const [results, setResults] = useState<Stock[]>([]);
  const [analyze, setAnalyst] = useState<StockAnalysis|null>(null);
  async function handleChange(event: ChangeEvent<HTMLTextAreaElement>) {
    const currentValue = event.target.value;
    
    console.log("Current textarea value:", currentValue);
    
    try {
      const response = await fetch(`https://api.stockanalysis.com/api/search?q=${currentValue}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const jsonResponse: ApiResponse = await response.json();
      
      // Extract the array of Stock objects from the data property
      setResults(jsonResponse.data);
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
      setResults([]);
    }
  }

  async function handleClick(symbol: string) {
    try {
      const response = await fetch(`/api/analyze?symbol=${symbol}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setAnalyst(data);
      // Handle the response data as needed
    } catch (error) {
      console.error("There was a problem with the analysis fetch operation:", error);
    }
  }

  return (
    <div>
      <Textarea 
        onChange={handleChange} 
        id="stock" 
        placeholder="search for some stocks"
      />
      {results.length > 0 && (
        <ul>
          {results.map((stock, index) => (
            <li key={index} onClick={() => handleClick(stock.s)}>
              {stock.s} - {stock.n} ({stock.t})
            </li>
          ))}
        </ul>
      )}
      { analyze && (
        <span>{analyze.analysis}</span>
      )}
    </div>
  );
}
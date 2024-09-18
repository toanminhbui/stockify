'use client'
import React, { ChangeEvent, useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from "./card";
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
  const [processing, setProcessing] = useState<boolean>(false);
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
      setProcessing(true);
      setResults([])
      setAnalyst(null);
      const response = await fetch(`/api/analyze?symbol=${symbol}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setAnalyst(data);
      setProcessing(false);
      // Handle the response data as needed
    } catch (error) {
      console.error("There was a problem with the analysis fetch operation:", error);
    }
  }

  return (
    <div>
    <h1 className="text-3xl font-serif">WallStreet Corners</h1>
      <Textarea 
        onChange={handleChange} 
        id="stock" 
        placeholder="search up some publicly listed stocks"
        className="font-serif"
      />
      {results.length > 0 && (
        <ul>
          {results.map((stock, index) => (
            <li key={index} onClick={() => handleClick(stock.s)}>
              {stock.s} - {stock.n} 
            </li>
          ))}
        </ul>
      )}
        {processing &&
        (
            <span>Please wait, analyst compiling news...</span>
        )

        }
      { analyze && (
        <div>
            <Card>
                <CardHeader>
                    <CardTitle>{analyze.symbol} Stock Price</CardTitle>
                    <CardDescription>Recent market movement</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col">
                    <span>Current Price: {analyze.current_price}</span>
                    <span>Price Change: {analyze.price_change}</span>
                    <span>Percent Change: {analyze.percent_change}</span>
                </CardContent>
            </Card>
            <h2 className="text-bold text-xl mt-10">Analyst Overview</h2>
            <span>{analyze.analysis}</span>
            <h2 className="text-bold text-xl mt-10">Market Movement Analysis</h2>
            <span>{analyze.market_sentiment}</span>
        </div>
      )}
    </div>
  );
}
import { Textarea } from "@/components/ui/textarea"
import { useState } from "react"

export default function SearchBar() {
    const [searchValue, setSearchValue] = useState("")

    function handleChange(event) {
        const newValue = event.target.value
        setSearchValue(newValue)
        
        // Now you can do something with the value
        console.log("Current textarea value:", newValue)
        
        // You can perform any other operations with newValue here
    }

    return (
        <Textarea 
            onChange={handleChange} 
            id="stock" 
            placeholder="search for some stocks"
            value={searchValue}
        />
    )
}
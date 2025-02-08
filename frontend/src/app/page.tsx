"use client";

import React, { useState } from "react";
import { IBM_Plex_Mono } from "@next/font/google";

// Inline SVG chevrons for the instructions box
function ChevronDownIcon() {
  return (
    <svg
      className="w-5 h-5"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
    </svg>
  );
}

function ChevronUpIcon() {
  return (
    <svg
      className="w-5 h-5"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
    </svg>
  );
}

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
});

export default function HomePage() {
  const [mantra, setMantra] = useState("");
  const [ghanam, setGhanam] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  // Toggle for collapsible instructions
  const [showInstructions, setShowInstructions] = useState(false);

  async function handleConvert() {
    try {
      setLoading(true);
      setErrorMsg("");
      setGhanam("");

      // Adjust URL if needed
      const response = await fetch("http://127.0.0.1:5000/transform", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mantra }),
      });

      if (!response.ok) {
        throw new Error("Server returned a non-OK status");
      }

      const data = await response.json();
      if (data.ghanam) {
        setGhanam(data.ghanam);
      } else if (data.error) {
        setErrorMsg(data.error);
      } else {
        setErrorMsg("Unexpected response from server.");
      }
    } catch (error: any) {
      console.error(error);
      setErrorMsg(error.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      className={`
        ${ibmPlexMono.className}
        bg-[#17171A]
        min-h-screen
        text-white
        flex
        flex-col
        items-center
        justify-center
        p-6
        text-center
      `}
    >
      <div className="max-w-2xl w-full flex flex-col gap-6">
        
        {/* Heading */}
        <div>
          <h1 className="text-2xl font-bold mb-1">Mantra to Ghanam Converter</h1>
          <p className="text-gray-400 text-sm">
            a tool to convert vedic mantras to the ghanam style
          </p>
        </div>

        {/* Textarea + Convert Button */}
        <div className="flex flex-col w-full items-center">
          <div className="relative w-full">
            <textarea
              value={mantra}
              onChange={(e) => setMantra(e.target.value)}
              placeholder="Paste mantra here"
              // Remove placeholder on focus, restore if empty on blur
              onFocus={(e) => (e.target.placeholder = "")}
              onBlur={(e) => {
                if (!mantra.trim()) {
                  e.target.placeholder = "Paste mantra here";
                }
              }}
              className="
                w-full
                h-16                /* 4rem tall */
                bg-[#1D1D1F]
                text-white
                text-sm
                text-left           /* horizontally aligned left */
                rounded
                focus:outline-none
                focus:ring-2
                focus:ring-blue-500
                px-3
                py-0
                pr-20
                leading-[4rem]     /* line-height to match h-16 */
                placeholder:leading-[4rem]
              "
            />
            <button
              onClick={handleConvert}
              disabled={loading}
              className="
                absolute
                top-3
                right-3
                bg-white
                text-black
                hover:bg-gray-200
                py-2
                px-4
                rounded
                font-semibold
                text-sm
                disabled:opacity-50
              "
            >
              {loading ? "Converting..." : "Convert"}
            </button>
          </div>
        </div>

        {/* Collapsible Instructions with white border */}
        <div className="flex flex-col w-full items-center">
          <div
            className="
              w-full
              border
              border-white
              bg-[#1D1D1F]
              text-white
              text-sm
              py-2
              px-3
              rounded
              text-left
            "
          >
            {/* Header row for toggling instructions */}
            <div
              className="flex items-center justify-between cursor-pointer"
              onClick={() => setShowInstructions(!showInstructions)}
            >
              <span className="font-bold">Instructions</span>
              {showInstructions ? <ChevronUpIcon /> : <ChevronDownIcon />}
            </div>

            {/* Formatted Instructions */}
            {showInstructions && (
              <div className="mt-2 text-left">
                <h3 className="text-md font-bold mb-2">
                  How to Use the Mantra to Ghanam Converter
                </h3>
                <ol className="list-decimal list-inside space-y-2 text-sm">
                  <li>
                    <span className="font-bold">Enter Your Mantra:</span> In the large text field on the page, paste or type your mantra.
                    <br />
                    <span className="italic">Tip:</span> You can include the <code>|</code> character to mark specific segments (this is optional).
                  </li>
                  <li>
                    <span className="font-bold">Submit Your Mantra:</span> Once you have entered your text, click the <span className="font-semibold">Convert</span> button below the text field.
                  </li>
                  <li>
                    <span className="font-bold">View the Transformed Text:</span> After clicking the button, the application will process your input and display the transformed (Ghanam) version of your mantra below the form.
                  </li>
                  <li>
                    <span className="font-bold">Try Again:</span> If you’d like to convert a different mantra, simply update the text in the field and click <span className="font-semibold">Convert</span> again.
                  </li>
                </ol>
              </div>
            )}
          </div>
        </div>

        {/* Error Message */}
        {errorMsg && (
          <p className="text-red-400 bg-red-900/30 p-2 text-sm rounded">
            {errorMsg}
          </p>
        )}

        {/* Converted Text */}
        {ghanam && (
          <div className="bg-[#1D1D1F] p-3 rounded mt-4">
            <h2 className="text-lg font-bold mb-2">Ghanam Result:</h2>
            <p className="whitespace-pre-wrap text-sm">{ghanam}</p>
          </div>
        )}
      </div>
    </main>
  );
}


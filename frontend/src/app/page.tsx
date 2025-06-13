"use client";
import React, { useState, useRef } from "react";

const API_BASE = "http://localhost:8000/api";

type MatchResult = {
  overall_match: number;
  category_scores: Record<string, number>;
  missing_skills: string[];
  strengths: string[];
  recommendations: string[];
  skill_comparison_table: any[];
};

type Analysis = {
  resume_entities: any;
  jd_entities: any;
  match_result: MatchResult;
};

export default function Home() {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [reportUrl, setReportUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Drag-and-drop handlers
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setResumeFile(e.dataTransfer.files[0]);
    }
  };
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  // File input handler
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setResumeFile(e.target.files[0]);
    }
  };

  // Analyze resume and JD
  const handleAnalyze = async () => {
    if (!resumeFile || !jdText) return;
    setAnalyzing(true);
    setAnalysis(null);
    setReportUrl(null);
    const formData = new FormData();
    formData.append("resume_file", resumeFile);
    formData.append("job_description", jdText);
    const res = await fetch(`${API_BASE}/analyze/match`, {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setAnalysis(data);
    setAnalyzing(false);
  };

  // Generate PDF report
  const handleGenerateReport = async () => {
    if (!analysis?.match_result) return;
    const res = await fetch(`${API_BASE}/reports/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ match_result: analysis.match_result }),
    });
    const data = await res.json();
    setReportUrl(data.pdf_url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white/90 rounded-2xl shadow-2xl p-8 mt-8 mb-8">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-700 to-purple-600 mb-6 tracking-tight uppercase drop-shadow-lg">
          RJD Parser
        </h1>
        <div className="flex flex-col gap-6">
          {/* Resume Upload */}
          <div
            className="border-2 border-dashed border-blue-400 rounded-lg p-6 text-center cursor-pointer bg-blue-50 hover:bg-blue-100 transition"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              className="hidden"
              ref={fileInputRef}
              onChange={handleFileChange}
            />
            {resumeFile ? (
              <span className="font-semibold text-blue-700">{resumeFile.name}</span>
            ) : (
              <span className="text-gray-500">Drag & drop your resume here, or click to select (PDF, DOC, DOCX)</span>
            )}
          </div>
          {/* JD Input */}
          <textarea
            className="w-full min-h-[120px] rounded-lg border border-purple-400 p-4 text-base focus:outline-none focus:ring-2 focus:ring-purple-500 bg-purple-50 placeholder:text-gray-500 text-gray-800"
            placeholder="Paste the job description here..."
            value={jdText}
            onChange={e => setJdText(e.target.value)}
          />
          {/* Analyze Button */}
          <button
            className="w-full py-3 rounded-lg bg-gradient-to-r from-blue-700 to-purple-600 text-white font-bold text-lg shadow-lg hover:scale-105 transition disabled:opacity-50"
            onClick={handleAnalyze}
            disabled={!resumeFile || !jdText || analyzing}
          >
            {analyzing ? "Analyzing..." : "Analyze Resume & JD"}
          </button>
        </div>
        {/* Results */}
        {analysis && (
          <div className="mt-8 bg-white/80 rounded-xl p-6 shadow-inner animate-fade-in">
            <h2 className="text-xl font-bold text-blue-800 mb-2">Results</h2>
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-800">Overall Match:</span>
                <span className="text-2xl font-extrabold text-purple-800">{analysis.match_result.overall_match}%</span>
              </div>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {Object.entries(analysis.match_result.category_scores).map(([cat, score]) => (
                  <div key={cat} className="flex items-center gap-2">
                    <span className="capitalize text-gray-800">{cat.replace('_', ' ')}:</span>
                    <span className="font-bold text-blue-800">{score}%</span>
                  </div>
                ))}
              </div>
              <div className="mt-4">
                <span className="font-semibold text-green-700">Strengths:</span>
                <span className="ml-2 text-gray-800">{analysis.match_result.strengths.length ? analysis.match_result.strengths.join(", ") : "None"}</span>
              </div>
              <div className="mt-2">
                <span className="font-semibold text-red-700">Missing Skills:</span>
                <span className="ml-2 text-gray-800">{analysis.match_result.missing_skills.length ? analysis.match_result.missing_skills.join(", ") : "None"}</span>
              </div>
            </div>
            {/* Recommendations Section - Rendered Separately for Type Safety */}
            {analysis && analysis.match_result && (
              <div className="mt-2">
                <span className="font-semibold text-purple-700">Recommendations:</span>
                <ul className="list-disc ml-8 text-gray-800">
                  {(Array.isArray(analysis?.match_result?.recommendations) && analysis.match_result.recommendations.length > 0)
                    ? (analysis.match_result.recommendations as string[]).map((rec: string, i: number) => <li key={i}>{rec}</li>)
                    : <li key="none">None</li>
                  }
                </ul>
              </div>
            )}
            {analysis && analysis.match_result && analysis.match_result.skill_comparison_table && (
              <div className="mt-6">
                <h3 className="text-lg font-bold text-blue-700 mb-2">Skill Comparison</h3>
                <div className="overflow-x-auto rounded-lg shadow">
                  <table className="min-w-full bg-white border border-gray-200">
                    <thead>
                      <tr>
                        <th className="px-4 py-2 border-b text-left text-gray-800 font-semibold bg-gray-100">Skill</th>
                        <th className="px-4 py-2 border-b text-center text-gray-800 font-semibold bg-gray-100">Required</th>
                        <th className="px-4 py-2 border-b text-center text-gray-800 font-semibold bg-gray-100">Present</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysis.match_result.skill_comparison_table.map((row: any, idx: number) => (
                        <tr key={row.skill} className={idx % 2 === 0 ? "bg-gray-50" : "bg-white"}>
                          <td className="px-4 py-2 border-b font-mono text-sm text-gray-800">{row.skill}</td>
                          <td className="px-4 py-2 border-b text-center text-gray-800 font-semibold">
                            {row.required ? (
                              <span className="text-green-600 font-bold">&#10003;</span>
                            ) : (
                              <span className="text-red-500 font-bold">&#10007;</span>
                            )}
                          </td>
                          <td className="px-4 py-2 border-b text-center text-gray-800 font-semibold">
                            {row.present ? (
                              <span className="text-green-600 font-bold">&#10003;</span>
                            ) : (
                              <span className="text-red-500 font-bold">&#10007;</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            <button
              className="mt-6 w-full py-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-700 text-white font-bold shadow hover:scale-105 transition"
              onClick={handleGenerateReport}
            >
              Generate PDF Report
            </button>
            {reportUrl && (
              <div className="mt-4 text-center">
                <a
                  href={`http://localhost:8000/${reportUrl}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-700 underline font-semibold hover:text-purple-700"
                >
                  Download PDF Report
                </a>
              </div>
            )}
          </div>
        )}
      </div>
      <footer className="text-white/80 text-center mt-8 text-xs">
        <span>RJD Parser [Resume - Job Description Parser] &copy; {new Date().getFullYear()} | Built with Next.js, FastAPI, and ML/NLP</span>
      </footer>
    </div>
  );
}

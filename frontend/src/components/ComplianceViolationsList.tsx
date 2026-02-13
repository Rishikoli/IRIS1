
import React, { useState } from 'react';
import { FiAlertTriangle, FiAlertCircle, FiCheckCircle, FiChevronDown, FiChevronUp, FiBookOpen } from 'react-icons/fi';

interface Violation {
    framework: string;
    rule_id: string;
    rule_description: string;
    severity: string;
    violation_description: string;
    evidence: any;
    remediation_steps: string[];
    regulatory_reference: string;
}

interface ComplianceViolationsListProps {
    violations: Violation[];
}

const ComplianceViolationsList: React.FC<ComplianceViolationsListProps> = ({ violations }) => {
    const [expandedId, setExpandedId] = useState<string | null>(null);

    if (!violations || violations.length === 0) {
        return (
            <div className="p-8 text-center bg-white rounded-2xl border border-slate-100">
                <div className="inline-flex p-3 bg-emerald-50 rounded-full mb-3">
                    <FiCheckCircle className="w-6 h-6 text-emerald-500" />
                </div>
                <h3 className="text-lg font-medium text-slate-800">No Violations Detected</h3>
                <p className="text-slate-500 text-sm mt-1">Great job! No significant compliance issues found.</p>
            </div>
        );
    }

    const toggleExpand = (id: string) => {
        setExpandedId(expandedId === id ? null : id);
    };

    const getSeverityColor = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'critical': return 'bg-red-500 text-white';
            case 'high': return 'bg-orange-500 text-white';
            case 'medium': return 'bg-yellow-500 text-white';
            default: return 'bg-slate-500 text-white';
        }
    };

    const getSeverityIcon = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'critical': return <FiAlertTriangle />;
            case 'high': return <FiAlertCircle />;
            default: return <FiAlertCircle />;
        }
    };

    return (
        <div className="neumorphic-card rounded-2xl p-6 bg-white mt-6">
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-100">
                <div className="p-2 bg-red-50 rounded-lg">
                    <FiAlertTriangle className="w-6 h-6 text-red-500" />
                </div>
                <div>
                    <h3 className="text-xl font-bold text-slate-800">Compliance Violations</h3>
                    <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">DETAILED BREAKDOWN</p>
                </div>
                <div className="ml-auto">
                    <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-xs font-bold">
                        {violations.length} Issues Found
                    </span>
                </div>
            </div>

            <div className="space-y-3">
                {violations.map((violation, index) => {
                    const id = `${violation.rule_id}-${index}`;
                    const isExpanded = expandedId === id;

                    return (
                        <div key={id} className={`border rounded-xl transition-all duration-300 ${isExpanded ? 'border-red-200 shadow-md bg-red-50/10' : 'border-slate-100 hover:border-slate-200'}`}>
                            <div
                                className="p-4 cursor-pointer flex items-start gap-4"
                                onClick={() => toggleExpand(id)}
                            >
                                <div className={`shrink-0 p-2 rounded-lg ${getSeverityColor(violation.severity)}`}>
                                    {getSeverityIcon(violation.severity)}
                                </div>

                                <div className="flex-1">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{violation.framework}</span>
                                                <span className="text-xs px-2 py-0.5 bg-slate-100 text-slate-600 rounded font-mono">{violation.rule_id}</span>
                                            </div>
                                            <h4 className="font-semibold text-slate-800">{violation.rule_description}</h4>
                                        </div>
                                        <div className="text-slate-400">
                                            {isExpanded ? <FiChevronUp /> : <FiChevronDown />}
                                        </div>
                                    </div>

                                    {!isExpanded && (
                                        <p className="text-sm text-slate-600 mt-2 line-clamp-1">{violation.violation_description}</p>
                                    )}
                                </div>
                            </div>

                            {isExpanded && (
                                <div className="px-4 pb-4 pl-[4.5rem]">
                                    <div className="mt-2 p-3 bg-white rounded-lg border border-red-100 text-sm text-slate-700 mb-4">
                                        <h5 className="font-bold text-red-800 mb-1 text-xs uppercase">Violation Details</h5>
                                        {violation.violation_description}
                                    </div>

                                    {violation.regulatory_reference && (
                                        <div className="flex items-start gap-2 mb-4 text-xs text-slate-500">
                                            <FiBookOpen className="shrink-0 mt-0.5" />
                                            <span>Ref: {violation.regulatory_reference}</span>
                                        </div>
                                    )}

                                    {violation.remediation_steps && violation.remediation_steps.length > 0 && (
                                        <div>
                                            <h5 className="font-bold text-emerald-700 mb-2 text-xs uppercase">Recommended Remediation</h5>
                                            <ul className="space-y-2">
                                                {violation.remediation_steps.map((step, idx) => (
                                                    <li key={idx} className="flex items-start gap-2 text-sm text-slate-700">
                                                        <FiCheckCircle className="text-emerald-500 shrink-0 mt-0.5 w-4 h-4" />
                                                        <span>{step}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default ComplianceViolationsList;

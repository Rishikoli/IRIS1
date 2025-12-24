
import React from 'react';
import { CheckCircle, Clock, Calendar, AlertCircle } from 'lucide-react';

interface AuditEvent {
    date: string;
    type: 'past' | 'current' | 'future';
    status: 'compliant' | 'violation' | 'pending' | 'scheduled';
    title: string;
    notes?: string;
}

interface AuditTimelineProps {
    nextDate?: string;
    events?: AuditEvent[];
}

const AuditTimeline: React.FC<AuditTimelineProps> = ({ nextDate, events }) => {
    // Use dynamic events if available, otherwise use a fallback with nextDate
    const timeline: AuditEvent[] = events || [
        { date: 'Q1 2024', type: 'past', status: 'compliant', title: 'Annual Audit', notes: 'Clean Report' },
        { date: 'Q2 2024', type: 'past', status: 'violation', title: 'Quarterly Review', notes: 'Minor discrepancies' },
        { date: 'Today', type: 'current', status: 'pending', title: 'Live Assessment', notes: 'In Progress' },
        { date: nextDate || 'Q1 2025', type: 'future', status: 'scheduled', title: 'Next Statutory Audit', notes: 'Due' },
    ];

    return (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 h-full">
            <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-purple-500" /> Audit Timeline
            </h3>

            <div className="relative">
                {/* Connecting Line */}
                <div className="absolute left-6 top-2 bottom-2 w-0.5 bg-slate-200"></div>

                <div className="space-y-6">
                    {timeline.map((event, index) => {
                        let Icon = CheckCircle;
                        let colorClass = 'bg-green-100 text-green-600 border-green-200';
                        let dotClass = 'bg-green-500 ring-green-200';

                        if (event.status === 'violation') {
                            Icon = AlertCircle;
                            colorClass = 'bg-red-50 text-red-600 border-red-200';
                            dotClass = 'bg-red-500 ring-red-200';
                        } else if (event.status === 'pending') {
                            Icon = Clock;
                            colorClass = 'bg-blue-50 text-blue-600 border-blue-200';
                            dotClass = 'bg-blue-500 ring-blue-200 animate-pulse';
                        } else if (event.status === 'scheduled') {
                            Icon = Calendar;
                            colorClass = 'bg-slate-50 text-slate-500 border-slate-200';
                            dotClass = 'bg-slate-300 ring-slate-100';
                        }

                        return (
                            <div key={index} className="relative flex items-start gap-4 z-10">
                                {/* Dot */}
                                <div className={`w-3 h-3 rounded-full mt-2 ring-4 ${dotClass}`}></div>

                                {/* Card */}
                                <div className={`flex-1 p-3 rounded-xl border ${colorClass} transition-all hover:shadow-md`}>
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="font-bold text-sm">{event.date}</span>
                                        <Icon size={14} />
                                    </div>
                                    <div className="font-semibold text-sm">{event.title}</div>
                                    {event.notes && <div className="text-xs opacity-80 mt-1">{event.notes}</div>}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default AuditTimeline;

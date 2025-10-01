import React from 'react';

interface FeaturedArticleProps {
  category: string;
  timeAgo: string;
  title: string;
  tags: string[];
}

export default function FeaturedArticle({ category, timeAgo, title, tags }: FeaturedArticleProps) {
  return (
    <div className="relative bg-gradient-to-br from-purple-100 via-blue-50 to-purple-50 rounded-3xl p-8 overflow-hidden">
      {/* Decorative gradient orb */}
      <div className="absolute right-0 top-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-purple-300/40 via-blue-300/40 to-transparent rounded-full blur-3xl" />
      
      <div className="relative z-10">
        <div className="inline-block px-3 py-1 bg-white rounded-full text-xs font-medium mb-4">
          BEST OF THE WEEK
        </div>
        
        <div className="text-sm text-gray-600 mb-2">
          {category} · {timeAgo}
        </div>
        
        <h1 className="text-4xl md:text-5xl font-bold mb-6 leading-tight max-w-xl">
          {title}
        </h1>
        
        <div className="flex gap-3 mb-6">
          {tags.map((tag, index) => (
            <span key={index} className="text-sm text-purple-600">
              #{tag}
            </span>
          ))}
        </div>
        
        <button className="flex items-center gap-2 text-sm font-medium hover:gap-3 transition-all">
          Read article
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}

import React from 'react';
import Image from 'next/image';

interface RecommendedArticleProps {
  title: string;
  category: string;
  timeAgo: string;
  imageUrl?: string;
}

export default function RecommendedArticle({ title, category, timeAgo, imageUrl }: RecommendedArticleProps) {
  return (
    <div className="flex gap-3 p-3 hover:bg-gray-50 rounded-xl transition-colors cursor-pointer">
      <div className="flex-1">
        <div className="text-xs text-gray-500 mb-1">
          {category} · {timeAgo}
        </div>
        <h4 className="text-sm font-medium leading-snug line-clamp-2">
          {title}
        </h4>
      </div>
      <div className="w-16 h-16 bg-gradient-to-br from-purple-200 to-blue-200 rounded-xl flex-shrink-0 overflow-hidden">
        {imageUrl && (
          <Image 
            src={imageUrl} 
            alt={title}
            width={64}
            height={64}
            className="w-full h-full object-cover"
          />
        )}
      </div>
    </div>
  );
}

import React from 'react';

interface ArticleCardProps {
  title: string;
  category?: string;
}

export default function ArticleCard({ title, category }: ArticleCardProps) {
  return (
    <div className="bg-white rounded-2xl p-4 hover:shadow-lg transition-shadow cursor-pointer">
      <div className="w-full h-32 bg-gradient-to-br from-purple-200 to-blue-200 rounded-xl mb-3" />
      <h3 className="text-sm font-medium leading-snug line-clamp-2">
        {title}
      </h3>
      {category && (
        <p className="text-xs text-gray-500 mt-2">{category}</p>
      )}
    </div>
  );
}

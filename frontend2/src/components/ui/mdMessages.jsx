import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';  // Import the remark-gfm plugin
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const MarkdownMessage = ({ content }) => {
  return (
    <ReactMarkdown
      children={content}
      remarkPlugins={[remarkGfm]}  // Use the remark-gfm plugin
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <SyntaxHighlighter
              style={oneDark}
              language={match[1]}
              PreTag="div"
              customStyle={{
                borderRadius: '0.5rem',
                padding: '1rem',
                backgroundColor: '#2d2d2d',
                color: 'hsl(142, 76%, 36%)',
                fontSize: '0.95rem',
                lineHeight: '1.5',
                whiteSpace: 'pre-wrap',
                wordWrap: 'break-word',
                boxShadow: '0 0 15px hsl(142, 76%, 36%)',
                transition: 'box-shadow 0.3s ease-in-out',
              }}
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code
              className={className}
              style={{
                backgroundColor: '#2d2d2d',
                padding: '0.2rem 0.4rem',
                borderRadius: '4px',
                fontSize: '0.95rem',
                color: 'hsl(142, 76%, 36%)',
              }}
              {...props}
            >
              {children}
            </code>
          );
        },
      }}
    />
  );
};

export default MarkdownMessage;

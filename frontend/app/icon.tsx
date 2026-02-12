import { ImageResponse } from 'next/og';

export const size = { width: 32, height: 32 };
export const contentType = 'image/png';

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: 32,
          height: 32,
          borderRadius: 8,
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <svg
          width="22"
          height="22"
          viewBox="0 0 22 22"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Chain link – left */}
          <rect
            x="2"
            y="6"
            width="7"
            height="10"
            rx="3.5"
            stroke="#FFF991"
            strokeWidth="1.8"
            fill="none"
          />
          {/* Chain link – right */}
          <rect
            x="13"
            y="6"
            width="7"
            height="10"
            rx="3.5"
            stroke="#FFF991"
            strokeWidth="1.8"
            fill="none"
          />
          {/* Connecting bar between links */}
          <line
            x1="9"
            y1="11"
            x2="13"
            y2="11"
            stroke="#FFF991"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
          {/* Pulse line running through */}
          <polyline
            points="0,11 4,11 6,5 8,17 10,8 12,14 14,5 16,17 18,11 22,11"
            stroke="white"
            strokeWidth="1.4"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
            opacity="0.85"
          />
        </svg>
      </div>
    ),
    { ...size }
  );
}

import { ResumeOptimizerData } from '@/types/resumeOptimizer';

const resumeOptimizerData: ResumeOptimizerData = {
  profileName: 'Alex Chen',
  currentResumeScore: 82,
  optimizedResumeScore: 91,
  currentAtsScore: 74,
  optimizedAtsScore: 88,
  summary: {
    original:
      'Senior full-stack engineer with experience building scalable web applications and modern product experiences.',
    optimized:
      'Senior full-stack engineer specializing in high-scale React, Next.js, and distributed systems with a proven track record of shipping performant, user-centered products.',
  },
  projectHighlights: [
    {
      original: 'Built a real-time collaboration dashboard for 50k active users.',
      optimized:
        'Architected a real-time collaboration platform supporting 50k+ concurrent users with resilient WebSocket infrastructure and low-latency updates.',
    },
    {
      original: 'Improved page performance for a large marketing site using frontend optimizations.',
      optimized:
        'Reduced core web vitals and improved LCP by 68% through targeted frontend optimization, code-splitting, and rendering improvements.',
    },
  ],
  bulletPoints: [
    {
      original: 'Developed features for the company web application.',
      optimized:
        'Delivered end-to-end product features across frontend and backend services, improving reliability, developer velocity, and customer experience.',
    },
    {
      original: 'Worked with cloud infrastructure and deployment tools.',
      optimized:
        'Managed containerized deployments and CI/CD pipelines in AWS and Kubernetes environments to support rapid, repeatable releases.',
    },
  ],
  technicalKeywords: ['Next.js', 'TypeScript', 'WebSockets', 'System Design', 'CI/CD', 'Kubernetes', 'Performance Optimization', 'Distributed Systems'],
  missingSkills: ['GraphQL', 'gRPC', 'Observability', 'Auth0 / Okta'],
  missingSections: ['GitHub', 'LinkedIn', 'Portfolio', 'Certifications', 'Achievements'],
  suggestions: [
    {
      id: 's-1',
      title: 'Professional Summary',
      category: 'Summary',
      original: 'Senior full-stack engineer with experience building scalable web applications and modern product experiences.',
      optimized: 'Senior full-stack engineer specializing in high-scale React, Next.js, and distributed systems with a proven track record of shipping performant, user-centered products.',
      impact: '+12 ATS relevance',
      status: 'pending',
    },
    {
      id: 's-2',
      title: 'Project Impact',
      category: 'Projects',
      original: 'Built a real-time collaboration dashboard for 50k active users.',
      optimized: 'Architected a real-time collaboration platform supporting 50k+ concurrent users with resilient WebSocket infrastructure and low-latency updates.',
      impact: '+9 recruiter appeal',
      status: 'pending',
    },
    {
      id: 's-3',
      title: 'Bullet Improvement',
      category: 'Experience',
      original: 'Developed features for the company web application.',
      optimized: 'Delivered end-to-end product features across frontend and backend services, improving reliability, developer velocity, and customer experience.',
      impact: '+8 clarity score',
      status: 'pending',
    },
  ],
  timeline: [
    { title: 'Resume scanned', detail: 'Profile and role context extracted successfully.', time: '2 min ago' },
    { title: 'ATS gap analysis', detail: 'Keywords and missing sections mapped against target roles.', time: '1 min ago' },
    { title: 'Optimization draft ready', detail: 'Resume copy and bullet points rewritten for impact.', time: 'Just now' },
  ],
};

export const getResumeOptimizerData = (): ResumeOptimizerData => resumeOptimizerData;

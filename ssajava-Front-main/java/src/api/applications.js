/**
 * [설명]
 * - 지원서 제출/조회/상태 변경 등 API 모음.
 * - 백엔드 명세: /v1/applications
 */
import api from './client';

// 지원서 제출
export const submitApplication = (payload) => api.post('/applications', payload);

// 지원서 목록
export const getApplications = () => api.get('/applications');

// 지원서 상세
export const getApplication = (id) => api.get(`/applications/${id}`);

// 지원서 상태 변경
export const updateApplicationStatus = (id, status) =>
  api.put(`/applications/${id}/status`, { status });

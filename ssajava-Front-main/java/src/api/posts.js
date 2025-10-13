/**
 * [설명]
 * - 공고 CRUD와 공고별 질문 API 모음.
 * - 백엔드 명세: /v1/posts, /v1/posts/{postId}/questions
 */
import api from './client';

// 목록 조회 (필터/검색이 있으면 params로 전달)
export const getPosts = (params = {}) => api.get('/posts', { params });

// 단건 조회
export const getPost = (id) => api.get(`/posts/${id}`);

// 생성
export const createPost = (payload) => api.post('/posts', payload);

// 수정
export const updatePost = (id, payload) => api.put(`/posts/${id}`, payload);

// 삭제
export const deletePost = (id) => api.delete(`/posts/${id}`);

// 질문 조회/생성
export const getPostQuestions = (postId) => api.get(`/posts/${postId}/questions`);
export const createPostQuestions = (postId, questions) =>
  api.post(`/posts/${postId}/questions`, { questions });

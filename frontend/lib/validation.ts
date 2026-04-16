/**
 * Client-side validation utilities for forms
 */

export const validateEmail = (email: string): { valid: boolean; error?: string } => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!email.trim()) {
    return { valid: false, error: 'Email is required' }
  }
  if (!emailRegex.test(email)) {
    return { valid: false, error: 'Please enter a valid email address' }
  }
  return { valid: true }
}

export const validatePassword = (password: string): { valid: boolean; error?: string } => {
  if (!password) {
    return { valid: false, error: 'Password is required' }
  }
  if (password.length < 8) {
    return { valid: false, error: 'Password must be at least 8 characters' }
  }
  if (!/[A-Z]/.test(password)) {
    return { valid: false, error: 'Password must contain an uppercase letter' }
  }
  if (!/[0-9]/.test(password)) {
    return { valid: false, error: 'Password must contain a number' }
  }
  if (!/[!@#$%^&*]/.test(password)) {
    return { valid: false, error: 'Password must contain a special character (!@#$%^&*)' }
  }
  return { valid: true }
}

export const validateName = (name: string): { valid: boolean; error?: string } => {
  if (!name.trim()) {
    return { valid: false, error: 'Name is required' }
  }
  if (name.trim().length < 2) {
    return { valid: false, error: 'Name must be at least 2 characters' }
  }
  return { valid: true }
}

export const validatePasswordMatch = (
  password: string,
  confirmPassword: string
): { valid: boolean; error?: string } => {
  if (password !== confirmPassword) {
    return { valid: false, error: 'Passwords do not match' }
  }
  return { valid: true }
}

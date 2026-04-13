import { Component, OnInit, signal } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit {
  // Splash
  splashVisible = true;
  splashFading  = false;

  // Login
  form!: FormGroup;
  loading  = signal(false);
  showPass = signal(false);
  error    = signal<string | null>(null);

  constructor(private fb: FormBuilder, private router: Router) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      email:    ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(4)]],
    });

    // Splash: 2.5s display then fade out
    setTimeout(() => {
      this.splashFading = true;
      setTimeout(() => { this.splashVisible = false; }, 600);
    }, 2500);
  }

  login(): void {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    this.loading.set(true);
    this.error.set(null);

    // Simulate auth — replace with real API call
    setTimeout(() => {
      const { email, password } = this.form.value;
      if (email === 'admin@sparky.tn' && password === 'sparky2026') {
        this.router.navigate(['/home']);
      } else {
        this.error.set('Email ou mot de passe incorrect.');
        this.loading.set(false);
      }
    }, 1000);
  }

  togglePass(): void { this.showPass.update(v => !v); }
}

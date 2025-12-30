type LogLevel = 'info' | 'warn' | 'error';

class Logger {
  private log(level: LogLevel, message: string, ...args: any[]) {
    const timestamp = new Date().toISOString();
    switch (level) {
      case 'info':
        console.log(`[INFO] ${timestamp}: ${message}`, ...args);
        break;
      case 'warn':
        console.warn(`[WARN] ${timestamp}: ${message}`, ...args);
        break;
      case 'error':
        console.error(`[ERROR] ${timestamp}: ${message}`, ...args);
        break;
    }
  }

  info(message: string, ...args: any[]) {
    this.log('info', message, ...args);
  }

  warn(message: string, ...args: any[]) {
    this.log('warn', message, ...args);
  }

  error(message: string, ...args: any[]) {
    this.log('error', message, ...args);
  }
}

export const logger = new Logger();

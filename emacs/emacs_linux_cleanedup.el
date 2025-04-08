;;; init.el --- Emacs config for Brian

;; Disable package.el in favor of straight.el
(setq package-enable-at-startup nil)

;; Bootstrap straight.el
(defvar bootstrap-version)
(let ((bootstrap-file
       (expand-file-name "straight/repos/straight.el/bootstrap.el" user-emacs-directory))
      (bootstrap-version 6))
  (unless (file-exists-p bootstrap-file)
    (with-current-buffer
        (url-retrieve-synchronously
         "https://raw.githubusercontent.com/radian-software/straight.el/develop/install.el"
         'silent 'inhibit-cookies)
      (goto-char (point-max))
      (eval-print-last-sexp)))
  (load bootstrap-file nil 'nomessage))

;; Integrate use-package with straight.el
(straight-use-package 'use-package)

(setq straight-use-package-by-default t)  ;; Automatically use straight with use-package
(setq use-package-always-ensure nil)      ;; Don't use :ensure (we're using straight now)
(setq use-package-expand-minimally t)

;; Make <F5> reload init
(defun reload-init-file ()
  (interactive)
  (load-file user-init-file))
(global-set-key (kbd "<f5>") 'reload-init-file)

(setq fill-column 80)
(setq-default line-spacing 1)

;;; === THEMES ===
;; (use-package material-theme)
;; (load-theme 'material-light t)
;; Pick your poison; I'm leaving the default `misterioso` theme alone for now

;;; === VTERM ===
(use-package vterm)
(use-package multi-vterm)

;;; === TREEMACS ===
(use-package treemacs
  :defer t
  :config
  (treemacs-follow-mode t)
  (treemacs-filewatch-mode t)
  (treemacs-fringe-indicator-mode 'always)
  (setq treemacs-width 35)
  ;; Add more `setq` customizations as needed
  )

(use-package treemacs-projectile :after (treemacs projectile))
(use-package treemacs-icons-dired :hook (dired-mode . treemacs-icons-dired-enable-once))
(use-package treemacs-magit :after (treemacs magit))
(use-package treemacs-persp :after (treemacs persp-mode)
  :config (treemacs-set-scope-type 'Perspectives))
(use-package treemacs-tab-bar :after treemacs
  :config (treemacs-set-scope-type 'Tabs))

;;; === YAML ===
(use-package yaml-mode
  :mode ("\\.ya?ml\\'" . yaml-mode))

;;; === ORG ===
(setq org-agenda-files
      '("~/workspace/bdunbar_notes/todo/master.org"
        "~/workspace/bdunbar_notes/todo/daily.org"))

;;; === CUSTOM VARIABLES AND FACES ===
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(custom-enabled-themes '(leuven))
 '(ispell-dictionary nil)
 '(org-fontify-whole-heading-line t)
 '(package-selected-packages '(yaml-mode vterm use-package)))

(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )


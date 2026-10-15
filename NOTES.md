# Open questions

- **How learners get the sandbox.** Docker is itself a hurdle for someone new to Linux.
  Options for phase 5: an in-browser VM (v86), a hosted shell, or a one-line installer.
  Decide before the website ships.
- **Public repo hosting.** Serving the apt repo from anarchygames.org is publishing;
  needs an explicit go-ahead.
- **In the Black packaging.** Not yet confirmed as a course package.
- **Ubuntu ships uutils now.** Ubuntu 25.10+ replaced GNU coreutils with the Rust uutils.
  Option letters are mostly the same, but `--help` text differs, so a learner who goes
  from the sandbox to a recent Ubuntu machine will see different help pages. The `grep`
  words our hints use are only verified against GNU. Worth a short note in the course.

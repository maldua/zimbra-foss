# Maldua's Zimbra FOSS

## Overview

![Maldua's Zimbra FOSS Splash](images/zimbra-maldua-foss-splash.png)

**MALDUA'S Zimbra FOSS** brought to you by [BTACTIC, open source & cloud solutions](https://www.btactic.com).

Maldua's Zimbra FOSS is a community-driven, open-source build of the Zimbra Collaboration Suite. It provides ready-to-install tarballs.

---

## Releases / Downloads

| Version | Platform | Notes |
|---|---|---|
| 10.1.10.p3 | Ubuntu 22.04 | Stable, may include Pimbra patches |
| 10.0.16.p3 | RHEL 8 | Stable, may include Pimbra patches |

Visit [Zimbra Foss Downloads Page (from Maldua)](https://maldua.github.io/zimbra-foss/downloads.html) for the full **updated** list.

---

## Features

### End-User Features

- **Email & Messaging**: IMAP/POP3 support, conversation view, advanced search, spam and virus filtering.

![Email](images/end-user/email1.png)

- **Calendar & Scheduling**: Shared calendars, meeting invitations, resource scheduling, reminders.

![Calendar](images/end-user/calendar1.png)

- **Contacts & Address Book**: Personal and shared contacts, distribution lists.

![Contacts](images/end-user/contacts1.png)

- **Tasks & To-Dos**: Task creation, prioritization, due dates, and reminders.
- **File Storage & Collaboration**: Briefcase for file uploads and sharing.
- **Mobile & Web Access**: Web UI, mobile sync via CalDAV, CardDAV, and Imap.
- **Zimlets & Extensions**: Customizable extensions for email integration with other services.
- **Search & Archiving**: Full-text search, message tagging, and folder organization.

### Admin Console Features (Sysadmin)

- **User Management**: Add, remove, and manage user accounts, distribution lists, and aliases.

![Users](images/sysadmin/user1.png)

- **Domain Management**: Configure and maintain multiple domains.

![Domains](images/sysadmin/domain1.png)

- **Server & Services Monitoring**: Real-time monitoring of mailbox servers, MTA, and other Zimbra services.

![Monitoring](images/sysadmin/monitoring1.png)

- **Security Management**: Configure spam and virus protection, TLS/SSL, and authentication policies.
- **System Configuration**: Global settings for mail routing, quotas, and network policies.
- **Logging & Auditing**: Access logs, audit trails, and system health reports.
- **CLI & Scripting Support**: Manage users, servers, and configurations via `zmprov` and CLI commands.

---

## Documentation for Sysadmins

- Installation (TODO)
- How to upgrade from Zimbra OSE 8.8.15    to Zimbra FOSS 10.1.x  (TODO)
- How to upgrade from Zimbra FOSS 9.0.0.pX to Zimbra FOSS 10.1.x  (TODO)
- How to upgrade from Zimbra FOSS 10.0.x   to Zimbra FOSS 10.1.x  (TODO)

---

## Build system

- Maldua's Zimbra FOSS is built thanks to [zimbra-foss-builder](https://github.com/maldua/zimbra-foss-builder).

---

## Additional documentation

If you want to take over this project these are the documentation files that you should be reading:

- [Build Zimbra tgz installers thanks to Github Actions](BUILD-GITHUB-ACTION.md)
- [Generate downloads page from Releases data thanks to Github Actions](DOWNLOADS-GITHUB-ACTION.md)
- [Release instructions for the project maintainer](MAINTAINER-RELEASE.md)

---

## Security & Patches

Maldua's Zimbra FOSS often includes **Pimbra** patches. These are either security fixes patches or regular fixes patches. In the worst case scenario we are two months behind Zimbra security fixes wise because those are [embargoed by Zimbra](https://wiki.zimbra.com/wiki/Zimbra_Foss_Source_Code_Only_Releases).

---

## Community & Support

- GitHub: [maldua/zimbra-foss-builder issues page](https://github.com/maldua/zimbra-foss-builder)
- Forums / Feedback: Use [Zimbra forums](https://forums.zimbra.org/viewtopic.php?t=72655) or GitHub issues
- Release Notifications (Login to Github first): [Stable](https://github.com/maldua/zimbra-foss-builder/discussions/8), [Recent](https://github.com/maldua/zimbra-foss-builder/discussions/9), [Experimental](https://github.com/maldua/zimbra-foss-builder/discussions/10).

---

## Roadmap / Future Plans

- Support more Linux distributions
- Better documentation and CI

---

## License & Legal

- GPL-2.0 license
- Community builds, not official Zimbra/Synacor binaries
- No warranty of MERCHANTABILITY or FITNESS.

---

## About Zimbra

- **Zimbra Collaboration Suite (FOSS Edition)**: Email, calendar, contacts, file storage, mobile sync, web UI.
- **Why Zimbra FOSS?**: Open-source, flexible deployment, extensible via Zimlets, active community.
- **Official Zimbra Resources**: [Zimbra zm-build GitHub](https://github.com/Zimbra/zm-build)

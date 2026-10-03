from typing import List
try:
    from backend.models.schemas import ContextItem
except ImportError:
    from models.schemas import ContextItem

def generate_mock_context_database() -> List[ContextItem]:
    items: List[ContextItem] = []

    # =========================================================================
    # 1. CORE GOLDEN EVIDENCE (Directly matching Prof. Xavier / CCNCPS / FieldChain)
    # =========================================================================
    items.append(ContextItem(
        id="gmail_39281",
        source="gmail",
        type="email",
        timestamp="2026-09-18T16:45:00",
        people=["Prof. Xavier Vance", "alex@lab.edu"],
        entities=["FieldChain", "CCNCPS", "Distributed Systems", "Professor X"],
        content="Subject: Great meeting you at CCNCPS / FieldChain follow-up\nHi Alex, enjoyed our talk after the poster session. Let's definitely look into extending FieldChain's Byzantine consensus layer with adaptive sharding. Send me your updated benchmark numbers once ready.\nBest,\nProf. Xavier Vance (MIT CSAIL)",
        reliability=0.98,
        permissions=["personal"],
        provenance={"provider": "happenstance", "source_id": "39281", "thread_id": "th_8829", "subject": "Great meeting you at CCNCPS"}
    ))

    items.append(ContextItem(
        id="calendar_812",
        source="calendar",
        type="event",
        timestamp="2026-09-16T14:30:00",
        people=["Prof. Xavier Vance", "Alex Rivera"],
        entities=["CCNCPS", "FieldChain", "Coffee Chat", "Professor X"],
        content="Calendar Event: 30-min Coffee Chat with Prof. Xavier Vance\nLocation: Hall B Lobby, CCNCPS 2026, San Francisco\nNotes: Discussed FieldChain throughput benchmarks (18k TPS), consensus latency, and co-authoring a follow-up proposal for IEEE S&P.",
        reliability=0.96,
        permissions=["personal"],
        provenance={"provider": "happenstance", "source_id": "cal_812", "calendar": "Academic & Research"}
    ))

    items.append(ContextItem(
        id="drive_1092",
        source="drive",
        type="doc",
        timestamp="2026-09-28T11:15:00",
        people=["Alex Rivera", "Dev Team"],
        entities=["FieldChain", "Benchmark Results", "Adaptive Sharding", "Throughput"],
        content="Document: FieldChain_V2_Benchmark_Report_Sept2026.pdf\nSummary: Latest testbed results show 19.4k TPS across 128 nodes with 42ms finality under simulated network partition. Sharding overhead reduced by 28%. Ready for external peer review.",
        reliability=0.97,
        permissions=["personal"],
        provenance={"provider": "drive_mcp", "source_id": "doc_1092", "path": "/Research/FieldChain/Benchmarks_v2.pdf"}
    ))

    items.append(ContextItem(
        id="contacts_404",
        source="contacts",
        type="contact",
        timestamp="2026-09-16T17:00:00",
        people=["Prof. Xavier Vance"],
        entities=["MIT CSAIL", "Professor", "Distributed Systems Lab", "Professor X"],
        content="Contact Card: Prof. Xavier Vance\nTitle: Associate Professor of Computer Science, MIT CSAIL\nEmail: xvance@csail.mit.edu\nResearch focus: Byzantine Fault Tolerance, Decentralized Consensus, Asynchronous State Machine Replication",
        reliability=0.99,
        permissions=["personal"],
        provenance={"provider": "happenstance", "source_id": "contact_404"}
    ))

    items.append(ContextItem(
        id="gmail_40112",
        source="gmail",
        type="email",
        timestamp="2026-09-20T09:20:00",
        people=["CCNCPS Organizing Committee", "Alex Rivera"],
        entities=["CCNCPS", "Best Poster Runner-up", "FieldChain"],
        content="Subject: CCNCPS 2026 Award Announcement\nCongratulations! Your poster 'FieldChain: Resilient Consensus via Adaptive Sharding' was awarded Best Poster Runner-Up in the Distributed Systems track.",
        reliability=0.97,
        permissions=["personal"],
        provenance={"provider": "happenstance", "source_id": "40112", "thread_id": "th_9104"}
    ))

    items.append(ContextItem(
        id="linkedin_5521",
        source="linkedin",
        type="post",
        timestamp="2026-09-17T18:00:00",
        people=["Alex Rivera", "Prof. Xavier Vance"],
        entities=["CCNCPS", "FieldChain", "Poster Session", "Professor X"],
        content="LinkedIn Connection: Prof. Xavier Vance accepted your connection request. Added note: 'Terrific poster presentation today Alex, let's keep in touch regarding the consensus evaluation.'",
        reliability=0.94,
        permissions=["public"],
        provenance={"provider": "happenstance", "source_id": "li_5521"}
    ))

    items.append(ContextItem(
        id="drive_881",
        source="drive",
        type="doc",
        timestamp="2026-09-14T20:00:00",
        people=["Alex Rivera"],
        entities=["FieldChain", "Presentation Slides", "CCNCPS"],
        content="Slide Deck: FieldChain_CCNCPS_Presentation.pptx\nSlide 14: Future Work & Open Questions — Adaptive sharding boundaries, cross-shard atomicity, and collaboration with MIT CSAIL consensus testbed.",
        reliability=0.95,
        permissions=["personal"],
        provenance={"provider": "drive_mcp", "source_id": "doc_881", "path": "/Talks/2026/CCNCPS_Slides.pptx"}
    ))

    items.append(ContextItem(
        id="calendar_810",
        source="calendar",
        type="event",
        timestamp="2026-09-15T09:00:00",
        people=["Alex Rivera", "Prof. Xavier Vance"],
        entities=["CCNCPS", "Keynote", "Professor X"],
        content="Calendar Event: CCNCPS 2026 Opening Keynote by Prof. Xavier Vance on 'Zero-Overhead Proofs in P2P Nets'. Attended Q&A session.",
        reliability=0.93,
        permissions=["personal"],
        provenance={"provider": "happenstance", "source_id": "cal_810"}
    ))

    items.append(ContextItem(
        id="gmail_39450",
        source="gmail",
        type="email",
        timestamp="2026-09-22T14:10:00",
        people=["Alex Rivera", "Dev Team"],
        entities=["FieldChain", "Code Freeze", "Benchmarks"],
        content="Subject: Testbed V2 code freeze completed\nHi Alex, the adaptive sharding branch is merged and all testbed nodes in AWS us-east are reporting consistent 19.4k TPS. All raw telemetry logs archived in Drive.",
        reliability=0.92,
        permissions=["personal"],
        provenance={"provider": "happenstance", "source_id": "39450"}
    ))

    # =========================================================================
    # 2. TOPICALLY ADJACENT / SECONDARY CANDIDATES (Evaluated in top 25)
    # =========================================================================
    items.append(ContextItem(
        id="gmail_38990",
        source="gmail",
        type="email",
        timestamp="2026-09-10T14:00:00",
        people=["Lab Director Dr. Singh", "Alex Rivera"],
        entities=["FieldChain", "Budget approval", "CCNCPS"],
        content="Subject: Conference travel approved for CCNCPS 2026. Make sure to connect with faculty working on distributed storage.",
        reliability=0.90,
        permissions=["personal"],
        provenance={"provider": "happenstance", "source_id": "38990"}
    ))

    items.append(ContextItem(
        id="drive_950",
        source="drive",
        type="doc",
        timestamp="2026-08-30T10:00:00",
        people=["Alex Rivera"],
        entities=["FieldChain", "Draft Paper"],
        content="Document: FieldChain_Architecture_Draft_v1.docx. Explains the dual-quorum consensus mechanism.",
        reliability=0.88,
        permissions=["personal"],
        provenance={"provider": "drive_mcp", "source_id": "doc_950"}
    ))

    items.append(ContextItem(
        id="calendar_799",
        source="calendar",
        type="event",
        timestamp="2026-09-14T19:00:00",
        people=["Alex Rivera", "Lab Colleagues"],
        entities=["CCNCPS", "Welcome Dinner"],
        content="Calendar Event: CCNCPS 2026 Welcome Reception & Poster Setup, San Francisco Marriott Marquis.",
        reliability=0.89,
        permissions=["personal"],
        provenance={"provider": "happenstance", "source_id": "cal_799"}
    ))

    items.append(ContextItem(
        id="linkedin_5510",
        source="linkedin",
        type="post",
        timestamp="2026-09-15T21:00:00",
        people=["Alex Rivera"],
        entities=["CCNCPS", "Keynote", "Xavier Vance"],
        content="LinkedIn Post: 'Inspiring keynote by Prof. Xavier Vance on verifiable consensus at CCNCPS today. Looking forward to presenting our poster on adaptive sharding tomorrow!'",
        reliability=0.91,
        permissions=["public"],
        provenance={"provider": "happenstance", "source_id": "li_5510"}
    ))

    # =========================================================================
    # 3. DISTRACTORS & NOISE (Building out the remaining candidates to reach exactly 200)
    # Target breakdown from PDR:
    # Gmail: 80
    # Calendar: 20
    # LinkedIn: 30
    # Drive: 50
    # Contacts: 20
    # Total = 200
    # =========================================================================

    # Generate remaining Gmail items to total 80
    gmail_distractors = [
        ("Uber Receipt: Ride to SF Airport", "Your receipt from Uber Technologies: $45.20", "2026-09-19T18:00:00"),
        ("United Airlines: Boarding pass for flight UA412", "Boarding pass to SFO. Seat 14B.", "2026-09-15T06:00:00"),
        ("Hilton Hotel San Francisco: Reservation Confirmation", "Confirmation #HIL8391 for CCNCPS stay.", "2026-09-14T12:00:00"),
        ("Amazon.com: Your package has been delivered", "Order #112-9849182 USB-C adapter delivered.", "2026-09-12T11:00:00"),
        ("GitHub: Security alert for dependencies", "Dependabot detected moderate vulnerability in lodash.", "2026-09-21T03:00:00"),
        ("IEEE Spectrum: Weekly Newsletter", "Top trends in quantum computing and neuromorphic hardware.", "2026-09-17T08:00:00"),
        ("Starbucks Rewards: Double Stars Day", "Come grab your favorite iced latte this Thursday!", "2026-09-16T07:30:00"),
        ("Gym Membership Renewal Notice", "Your monthly fitness pass will renew on October 1st.", "2026-09-22T09:00:00"),
        ("Substack: Pragmatic Engineer Dispatch #140", "Staff engineering archetypes and engineering ladders.", "2026-09-18T10:00:00"),
        ("DoorDash: 30% off your next ramen bowl", "Craving dinner? Order from Marufuku Ramen.", "2026-09-16T19:30:00"),
        ("Steam Autumn Sale Now Live", "Save up to 75% on selected strategy and indie titles.", "2026-09-23T18:00:00"),
        ("Electric Bill for August 2026", "Your monthly PG&E electric statement is ready: $68.40.", "2026-09-05T10:00:00"),
        ("Bank of America: Monthly Statement Available", "Your e-statement for checking account ending in 4102.", "2026-09-02T08:00:00"),
        ("Spotify: Discover Weekly Updated", "30 songs recommended based on your recent electronic listening.", "2026-09-21T06:00:00"),
        ("The New York Times Morning Briefing", "Global climate summit wraps up with new renewable targets.", "2026-09-24T07:00:00"),
    ]
    curr_gmail = len([x for x in items if x.source == "gmail"])
    for i in range(curr_gmail, 80):
        d_idx = i % len(gmail_distractors)
        subj, body, ts = gmail_distractors[d_idx]
        items.append(ContextItem(
            id=f"gmail_dist_{i+1000}",
            source="gmail",
            type="email",
            timestamp=ts,
            people=[f"service_{i}@example.com"],
            entities=["Noise", "Receipt", "Newsletter"],
            content=f"Subject: {subj} #{i}\n{body}\nRef: MSG-{10000+i}",
            reliability=0.70,
            permissions=["personal"],
            provenance={"provider": "happenstance", "source_id": f"dist_gm_{i}"}
        ))

    # Generate remaining Calendar items to total 20
    calendar_distractors = [
        ("Weekly Department Sync", "Department progress meeting in Room 402", "2026-09-10T11:00:00"),
        ("Dentist Appointment", "Routine cleaning at Bay Dental", "2026-09-08T15:00:00"),
        ("Gym - Cardio & Weights", "Personal workout session", "2026-09-17T06:30:00"),
        ("Dinner with college friends", "Italian bistro downtown", "2026-09-18T20:00:00"),
        ("Flight UA412 Departure", "Gate 72 SFO", "2026-09-15T08:15:00"),
        ("Apartment Maintenance Inspection", "Building HVAC system check", "2026-09-04T10:00:00"),
        ("Haircut Appointment", "Studio Barber 4th Street", "2026-09-12T16:00:00"),
        ("Sunday Farmers Market", "Local produce shopping", "2026-09-20T10:00:00"),
    ]
    curr_cal = len([x for x in items if x.source == "calendar"])
    for i in range(curr_cal, 20):
        d_idx = i % len(calendar_distractors)
        title, desc, ts = calendar_distractors[d_idx]
        items.append(ContextItem(
            id=f"calendar_dist_{i+2000}",
            source="calendar",
            type="event",
            timestamp=ts,
            people=["Alex Rivera"],
            entities=["Personal", "Calendar"],
            content=f"Event: {title}\nDetails: {desc}",
            reliability=0.82,
            permissions=["personal"],
            provenance={"provider": "happenstance", "source_id": f"dist_cal_{i}"}
        ))

    # Generate remaining LinkedIn items to total 30
    li_distractors = [
        ("Recruiter InMail from TechCorp", "Exciting Senior Distributed Systems role in Sunnyvale.", "2026-09-13T10:00:00"),
        ("Post liked by 14 people", "Your post on system benchmarking received 14 likes.", "2026-09-14T16:00:00"),
        ("Job Recommendation: Research Scientist", "Based on your profile: Research Scientist at Decentral Labs.", "2026-09-22T12:00:00"),
        ("Congratulations to David on 3 years at Stripe", "Congratulate your connection on their work anniversary.", "2026-09-11T09:00:00"),
        ("Trending in Tech: WebAssembly updates", "Discussion on browser JIT engines and Wasm GC proposal.", "2026-09-19T14:00:00"),
        ("Weekly Network Summary", "You appeared in 42 searches this week.", "2026-09-21T11:00:00"),
    ]
    curr_li = len([x for x in items if x.source == "linkedin"])
    for i in range(curr_li, 30):
        d_idx = i % len(li_distractors)
        title, desc, ts = li_distractors[d_idx]
        items.append(ContextItem(
            id=f"linkedin_dist_{i+3000}",
            source="linkedin",
            type="post",
            timestamp=ts,
            people=["LinkedIn Network"],
            entities=["LinkedIn", "Networking"],
            content=f"Notification: {title}\n{desc}",
            reliability=0.75,
            permissions=["public"],
            provenance={"provider": "happenstance", "source_id": f"dist_li_{i}"}
        ))

    # Generate remaining Drive items to total 50
    drive_distractors = [
        ("Tax_Documents_2025.pdf", "W-2 and deduction receipts for tax filing.", "2026-04-12T10:00:00"),
        ("Apartment_Lease_Agreement.pdf", "Standard 12 month lease signed with landlord.", "2025-08-01T14:00:00"),
        ("Car_Insurance_Policy.pdf", "Auto coverage renewal document.", "2026-05-15T09:00:00"),
        ("Recipe_Collection_Sourdough.docx", "Step by step baker percentage calculation.", "2025-11-20T17:00:00"),
        ("CS101_TA_Grading_Rubric.xlsx", "Grading matrix for homework assignment 3.", "2025-10-14T11:00:00"),
        ("Passport_Scan_Copy.pdf", "Identity documentation copy.", "2024-06-10T15:00:00"),
        ("Trip_Itinerary_Lake_Tahoe.docx", "Cabin booking and packing checklist.", "2025-12-18T19:00:00"),
        ("Bicycle_Repair_Manual.pdf", "Shimano gear derailleur adjustment guide.", "2025-04-03T11:00:00"),
        ("Resume_Old_Version_2024.pdf", "Prior CV before graduate lab enrollment.", "2024-08-20T16:00:00"),
        ("Home_Audio_Setup_Diagram.png", "5.1 surround sound wiring scheme.", "2025-02-14T13:00:00"),
    ]
    curr_dr = len([x for x in items if x.source == "drive"])
    for i in range(curr_dr, 50):
        d_idx = i % len(drive_distractors)
        filename, desc, ts = drive_distractors[d_idx]
        items.append(ContextItem(
            id=f"drive_dist_{i+4000}",
            source="drive",
            type="doc",
            timestamp=ts,
            people=["Alex Rivera"],
            entities=["Document", "Drive"],
            content=f"File: {filename}\nDescription: {desc}",
            reliability=0.80,
            permissions=["personal"],
            provenance={"provider": "drive_mcp", "source_id": f"dist_dr_{i}"}
        ))

    # Generate remaining Contacts items to total 20
    contact_distractors = [
        ("Sarah Miller (Bay Dental Reception)", "info@baydental.com", "2025-03-10T10:00:00"),
        ("Dave Wilson (Mechanic Auto Care)", "dave@autocare.com", "2025-06-11T14:00:00"),
        ("Emily Chang (College Roommate)", "emily.c@gmail.com", "2024-09-01T12:00:00"),
        ("Landlord Office Support", "maintenance@cityapartments.com", "2025-08-01T09:00:00"),
        ("Veterinarian Clinic", "vetcare@citypaws.com", "2025-07-22T11:00:00"),
        ("Dry Cleaner Express", "frontdesk@quickclean.com", "2025-09-14T15:00:00"),
    ]
    curr_ct = len([x for x in items if x.source == "contacts"])
    for i in range(curr_ct, 20):
        d_idx = i % len(contact_distractors)
        name, email, ts = contact_distractors[d_idx]
        items.append(ContextItem(
            id=f"contact_dist_{i+5000}",
            source="contacts",
            type="contact",
            timestamp=ts,
            people=[name],
            entities=["Contact", "AddressBook"],
            content=f"Contact Card: {name}\nEmail: {email}",
            reliability=0.88,
            permissions=["personal"],
            provenance={"provider": "happenstance", "source_id": f"dist_ct_{i}"}
        ))

    return items

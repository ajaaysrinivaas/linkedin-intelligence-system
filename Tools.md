Tool	Description	Status
get_person_profile	Get profile info with explicit section selection (experience, education, interests, honors, languages, certifications, skills, projects, contact_info, posts)	working
get_my_profile	Get the authenticated user's own LinkedIn profile (same sections as get_person_profile)	working
connect_with_person	Send a connection request or accept an incoming one, with optional note	#407
get_sidebar_profiles	Extract profile URLs from sidebar recommendation sections ("More profiles for you", "Explore premium profiles", "People you may know") on a profile page	working
get_inbox	List recent conversations from the LinkedIn messaging inbox	working
get_conversation	Read a specific messaging conversation by username or thread ID	working
search_conversations	Search messages by keyword	working
send_message	Send a message to a LinkedIn user (requires confirmation)	working
get_company_profile	Extract company information with explicit section selection (posts, jobs); about-section references may include a company_urn entry carrying the numeric id used by LinkedIn's people-search currentCompany URL facet	working
get_company_posts	Get recent posts from a company's LinkedIn feed	working
search_companies	Search for companies on LinkedIn by keywords	working
get_company_employees	List employees at a company from the /people/ page, with optional keyword filter	working
search_jobs	Search for jobs with keywords and location filters	working
search_people	Search for people by keywords, location, connection degree (1st/2nd/3rd), and current company	working
get_job_details	Get detailed information about a specific job posting	working
get_feed	Get recent posts from the authenticated user's home feed	working
close_session	Close browser session and clean up resources	working

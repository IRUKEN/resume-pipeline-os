use clap::Parser;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::fs;
use std::path::PathBuf;

#[derive(Parser, Debug)]
struct Args {
    #[arg(long)]
    profile: PathBuf,
    #[arg(long)]
    preferences: PathBuf,
    #[arg(long)]
    job: PathBuf,
    #[arg(long)]
    output: PathBuf,
}

#[derive(Debug, Deserialize)]
struct Profile {
    skills: Vec<String>,
    roles: Vec<String>,
    seniority: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct Preferences {
    preferred_roles: Vec<String>,
    preferred_work_modes: Vec<String>,
    preferred_seniority: Vec<String>,
    preferred_domains: Vec<String>,
    avoid: Vec<String>,
    minimum_scores: MinimumScores,
}

#[derive(Debug, Deserialize)]
struct MinimumScores {
    profile_score: u32,
    preference_score: u32,
}

#[derive(Debug, Deserialize)]
struct Job {
    company: String,
    role: String,
    location: String,
    raw_text: String,
    required_skills: Vec<String>,
    seniority: Vec<String>,
    work_mode: Vec<String>,
    years_experience: u32,
    requirements: Vec<String>,
}

#[derive(Debug, Serialize)]
struct DecisionReport {
    company: String,
    role: String,
    decision: String,
    hard_requirements_pass: bool,
    profile_score: u32,
    preference_score: u32,
    red_flags: Vec<String>,
    matched_skills: Vec<String>,
    missing_skills: Vec<String>,
    reasons: Vec<String>,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    let profile: Profile = read_json(&args.profile)?;
    let preferences: Preferences = read_json(&args.preferences)?;
    let job: Job = read_json(&args.job)?;
    let report = decide(&profile, &preferences, &job);

    if let Some(parent) = args.output.parent() {
        fs::create_dir_all(parent)?;
    }
    fs::write(&args.output, serde_json::to_string_pretty(&report)? + "\n")?;
    Ok(())
}

fn read_json<T: for<'de> Deserialize<'de>>(path: &PathBuf) -> Result<T, Box<dyn std::error::Error>> {
    let content = fs::read_to_string(path)?;
    Ok(serde_json::from_str(&content)?)
}

fn decide(profile: &Profile, preferences: &Preferences, job: &Job) -> DecisionReport {
    let profile_skills = normalized_set(&profile.skills);
    let job_skills = normalized_set(&job.required_skills);
    let matched_skills = sorted_intersection(&job_skills, &profile_skills);
    let missing_skills = sorted_difference(&job_skills, &profile_skills);

    let profile_score = profile_score(&matched_skills, &job_skills, profile, job);
    let preference_score = preference_score(preferences, job);
    let red_flags = red_flags(preferences, job);
    let hard_requirements_pass = hard_requirements_pass(job, &missing_skills);

    let apply = hard_requirements_pass
        && profile_score >= preferences.minimum_scores.profile_score
        && preference_score >= preferences.minimum_scores.preference_score
        && red_flags.is_empty();

    let mut reasons = Vec::new();
    reasons.push(format!(
        "Matched {} of {} detected skills.",
        matched_skills.len(),
        job_skills.len()
    ));
    if hard_requirements_pass {
        reasons.push("Hard requirements passed.".to_string());
    } else {
        reasons.push("Hard requirements did not pass.".to_string());
    }
    if !red_flags.is_empty() {
        reasons.push(format!("Detected red flags: {}.", red_flags.join(", ")));
    }

    DecisionReport {
        company: job.company.clone(),
        role: job.role.clone(),
        decision: if apply { "APPLY" } else { "SKIP" }.to_string(),
        hard_requirements_pass,
        profile_score,
        preference_score,
        red_flags,
        matched_skills,
        missing_skills,
        reasons,
    }
}

fn normalized_set(values: &[String]) -> HashSet<String> {
    values.iter().map(|value| value.to_lowercase()).collect()
}

fn sorted_intersection(left: &HashSet<String>, right: &HashSet<String>) -> Vec<String> {
    let mut values: Vec<String> = left.intersection(right).cloned().collect();
    values.sort();
    values
}

fn sorted_difference(left: &HashSet<String>, right: &HashSet<String>) -> Vec<String> {
    let mut values: Vec<String> = left.difference(right).cloned().collect();
    values.sort();
    values
}

fn profile_score(matched_skills: &[String], job_skills: &HashSet<String>, profile: &Profile, job: &Job) -> u32 {
    if job_skills.is_empty() {
        return 50;
    }
    let skill_ratio = matched_skills.len() as f32 / job_skills.len() as f32;
    let role_bonus = contains_any(&job.role, &profile.roles) as u32 * 10;
    let seniority_bonus = overlap(&profile.seniority, &job.seniority) as u32 * 5;
    ((skill_ratio * 90.0).round() as u32 + role_bonus + seniority_bonus).min(100)
}

fn preference_score(preferences: &Preferences, job: &Job) -> u32 {
    let mut score = 45;
    if contains_any(&job.role, &preferences.preferred_roles) {
        score += 25;
    }
    if overlap(&preferences.preferred_work_modes, &job.work_mode) {
        score += 15;
    }
    if overlap(&preferences.preferred_seniority, &job.seniority) {
        score += 10;
    }
    if contains_any(&job.raw_text, &preferences.preferred_domains) {
        score += 10;
    }
    score.min(100)
}

fn red_flags(preferences: &Preferences, job: &Job) -> Vec<String> {
    let haystack = format!("{} {} {} {}", job.role, job.location, job.raw_text, job.requirements.join(" ")).to_lowercase();
    let mut flags: Vec<String> = preferences
        .avoid
        .iter()
        .filter(|term| phrase_present(&haystack, term))
        .cloned()
        .collect();
    flags.sort();
    flags
}

fn hard_requirements_pass(job: &Job, missing_skills: &[String]) -> bool {
    if job.years_experience > 8 {
        return false;
    }
    let critical_missing = missing_skills
        .iter()
        .filter(|skill| matches!(skill.as_str(), "react" | "angular" | ".net" | "java" | "spring boot" | "sql"))
        .count();
    critical_missing <= 1
}

fn contains_any(haystack: &str, needles: &[String]) -> bool {
    let haystack = haystack.to_lowercase();
    needles.iter().any(|needle| haystack.contains(&needle.to_lowercase()))
}

fn overlap(left: &[String], right: &[String]) -> bool {
    let right_set = normalized_set(right);
    left.iter().any(|value| right_set.contains(&value.to_lowercase()))
}

fn phrase_present(haystack: &str, phrase: &str) -> bool {
    let phrase = phrase.to_lowercase();
    if phrase.contains(' ') {
        return haystack.contains(&phrase);
    }
    haystack
        .split(|ch: char| !ch.is_ascii_alphanumeric())
        .any(|token| token == phrase)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn profile() -> Profile {
        Profile {
            skills: vec!["react".into(), ".net".into(), "sql".into(), "docker".into()],
            roles: vec!["Full-Stack Developer".into(), "Platform Engineer".into()],
            seniority: vec!["senior".into(), "lead".into()],
        }
    }

    fn preferences() -> Preferences {
        Preferences {
            preferred_roles: vec!["platform engineer".into(), "full-stack".into()],
            preferred_work_modes: vec!["remote".into()],
            preferred_seniority: vec!["senior".into()],
            preferred_domains: vec!["platform".into()],
            avoid: vec!["junior".into(), "unpaid".into(), "onsite only".into()],
            minimum_scores: MinimumScores {
                profile_score: 75,
                preference_score: 70,
            },
        }
    }

    #[test]
    fn applies_when_scores_and_rules_pass() {
        let job = Job {
            company: "Example".into(),
            role: "Senior Platform Engineer".into(),
            location: "Remote".into(),
            raw_text: "remote senior platform react .net sql docker".into(),
            required_skills: vec!["react".into(), ".net".into(), "sql".into(), "docker".into()],
            seniority: vec!["senior".into()],
            work_mode: vec!["remote".into()],
            years_experience: 5,
            requirements: vec![],
        };
        let report = decide(&profile(), &preferences(), &job);
        assert_eq!(report.decision, "APPLY");
    }

    #[test]
    fn skips_when_red_flag_exists() {
        let mut job = Job {
            company: "Example".into(),
            role: "Junior Platform Engineer".into(),
            location: "Remote".into(),
            raw_text: "junior remote platform react .net sql docker".into(),
            required_skills: vec!["react".into(), ".net".into(), "sql".into(), "docker".into()],
            seniority: vec!["junior".into()],
            work_mode: vec!["remote".into()],
            years_experience: 1,
            requirements: vec![],
        };
        let report = decide(&profile(), &preferences(), &job);
        assert_eq!(report.decision, "SKIP");
        assert!(report.red_flags.contains(&"junior".to_string()));

        job.raw_text = "remote platform react .net sql docker".into();
        let report = decide(&profile(), &preferences(), &job);
        assert_eq!(report.decision, "SKIP");
    }

    #[test]
    fn red_flag_does_not_match_inside_larger_word() {
        let job = Job {
            company: "Example".into(),
            role: "Senior Platform Engineer".into(),
            location: "Remote".into(),
            raw_text: "build internal platform tools with react .net sql docker".into(),
            required_skills: vec!["react".into(), ".net".into(), "sql".into(), "docker".into()],
            seniority: vec!["senior".into()],
            work_mode: vec!["remote".into()],
            years_experience: 5,
            requirements: vec![],
        };
        let report = decide(&profile(), &preferences(), &job);
        assert!(!report.red_flags.contains(&"intern".to_string()));
    }
}
